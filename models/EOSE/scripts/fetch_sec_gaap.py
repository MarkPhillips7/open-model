#!/usr/bin/env python3
"""Pull EOSE GAAP actuals from SEC companyfacts and diff vs actuals.py.

Repeatable after each 10-Q / 10-K. Does not write the Google Sheet.

    python models/EOSE/scripts/fetch_sec_gaap.py
    python models/EOSE/scripts/fetch_sec_gaap.py --year 2026 --quarter 2

Adj. EBITDA, pipeline, and backlog are not in XBRL — copy those from the
earnings 8-K Ex. 99.1 listed in models/EOSE/sources.py.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from models.EOSE.actuals import ACTUALS  # noqa: E402
from models.EOSE.sources import (  # noqa: E402
    CIK,
    COMPANYFACTS_URL,
    GAAP_DURATION_TAGS,
    GAAP_INSTANT_TAGS,
    SCALE,
)

USER_AGENT = "open-model research bot contact@localhost"
QUARTER_ENDS = {
    1: (3, 31),
    2: (6, 30),
    3: (9, 30),
    4: (12, 31),
}


def _end(year: int, quarter: int) -> str:
    m, d = QUARTER_ENDS[quarter]
    return f"{year}-{m:02d}-{d:02d}"


def _frame_duration(year: int, quarter: int) -> str:
    if quarter == 4:
        return f"CY{year}"
    return f"CY{year}Q{quarter}"


def _frame_instant(year: int, quarter: int) -> str:
    return f"{_frame_duration(year, quarter)}I" if quarter != 4 else f"CY{year}Q4I"


def fetch_companyfacts() -> dict:
    req = urllib.request.Request(
        COMPANYFACTS_URL,
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
        if raw[:2] == b"\x1f\x8b":
            import gzip

            raw = gzip.decompress(raw)
        return json.loads(raw)


def _pick_duration(points: list[dict], year: int, quarter: int, *, allow_fy_residual: bool = True) -> float | None:
    """Quarter-only duration. Q4 is FY minus 9M when the 10-K has no Q4 frame."""
    end = _end(year, quarter)
    frame = _frame_duration(year, quarter)
    month, _day = QUARTER_ENDS[quarter]
    start = f"{year}-{month - 2:02d}-01"
    framed = [
        p
        for p in points
        if p.get("end") == end and p.get("frame") == frame and p.get("form") in ("10-Q", "10-K")
    ]
    # CY2025 is full-year — do not treat it as Q4.
    if quarter == 4:
        framed = [p for p in framed if p.get("start") == start]
    if framed:
        return float(framed[-1]["val"])
    q_only = [
        p
        for p in points
        if p.get("end") == end
        and p.get("start") == start
        and p.get("form") in ("10-Q", "10-K")
    ]
    if q_only:
        return float(q_only[-1]["val"])
    if quarter != 4 or not allow_fy_residual:
        return None
    fy = [
        p
        for p in points
        if p.get("end") == end
        and p.get("start") == f"{year}-01-01"
        and p.get("form") == "10-K"
    ]
    nine = [
        p
        for p in points
        if p.get("end") == f"{year}-09-30"
        and p.get("start") == f"{year}-01-01"
        and p.get("form") in ("10-Q", "10-K")
    ]
    if fy and nine:
        return float(fy[-1]["val"]) - float(nine[-1]["val"])
    return None


def _pick_instant(points: list[dict], year: int, quarter: int) -> float | None:
    end = _end(year, quarter)
    frame = _frame_instant(year, quarter)
    framed = [
        p
        for p in points
        if p.get("end") == end
        and p.get("form") in ("10-Q", "10-K")
        and (p.get("frame") in (frame, None) or (quarter == 4 and p.get("form") == "10-K"))
    ]
    # Prefer 10-K/10-Q with matching instant frame, else any 10-Q/10-K at end.
    for pref in (
        lambda p: p.get("form") in ("10-Q", "10-K") and p.get("frame") == frame,
        lambda p: p.get("form") == "10-K" and p.get("end") == end,
        lambda p: p.get("form") in ("10-Q", "10-K") and p.get("end") == end and p.get("start") is None,
    ):
        hits = [p for p in points if pref(p)]
        if hits:
            return float(hits[-1]["val"])
    return None


def gaap_for_quarter(facts: dict, year: int, quarter: int) -> dict[str, float]:
    usgaap = facts["facts"]["us-gaap"]
    out: dict[str, float] = {}

    def usd_or_shares(tag: str) -> list[dict]:
        units = usgaap[tag]["units"]
        if "USD" in units:
            return units["USD"]
        if "shares" in units:
            return units["shares"]
        return next(iter(units.values()))

    for tag, label in GAAP_DURATION_TAGS.items():
        if tag not in usgaap:
            continue
        allow_fy = label not in ("Basic shares", "Fully diluted shares")
        val = _pick_duration(usd_or_shares(tag), year, quarter, allow_fy_residual=allow_fy)
        if val is None:
            continue
        out[label] = round(val * SCALE[label], 6) if abs(val) >= 1 else val

    scratch: dict[str, float] = {}
    for tag, label in GAAP_INSTANT_TAGS.items():
        if tag not in usgaap:
            continue
        val = _pick_instant(usd_or_shares(tag), year, quarter)
        if val is None:
            continue
        if label.startswith("_"):
            scratch[label] = val
        else:
            out[label] = round(val * SCALE[label], 6)

    ltd_nc = scratch.get("_ltd_noncurrent")
    rp = scratch.get("_related_party_notes")
    if ltd_nc is not None and rp is not None:
        out["Long term debt"] = round((ltd_nc - rp) * 1e-6, 6)

    sga = out.get("SG&A")
    rd = out.get("R&D")
    if sga is not None and rd is not None and "ImpairmentOfLongLivedAssetsHeldForUse" in usgaap:
        wd = _pick_duration(
            usgaap["ImpairmentOfLongLivedAssetsHeldForUse"]["units"]["USD"],
            year,
            quarter,
            allow_fy_residual=True,
        )
        if wd is not None:
            out["OpEx"] = round(sga + rd + wd * 1e-6, 6)
    return out


def diff_row(label: str, sec: float | None, sheet: float | None) -> str:
    if sec is None and sheet is None:
        return ""
    if sec is None:
        return f"  {label:24} sheet={sheet}  (not in XBRL)"
    if sheet is None:
        return f"  {label:24} sec={sec}  MISSING from actuals.py"
    if abs(sec - sheet) > 0.02:
        return f"  {label:24} sec={sec}  actuals.py={sheet}  DRIFT"
    return f"  {label:24} {sec}  ok"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int)
    parser.add_argument("--quarter", type=int, choices=(1, 2, 3, 4))
    args = parser.parse_args()

    print(f"SEC companyfacts CIK{CIK}")
    facts = fetch_companyfacts()
    quarters = (
        [(args.year, args.quarter)]
        if args.year and args.quarter
        else sorted(ACTUALS)
    )
    for year, q in quarters:
        sec = gaap_for_quarter(facts, year, q)
        have = ACTUALS.get((year, q), {})
        print(f"\n{year} Q{q}")
        labels = sorted(set(sec) | {k for k in have if k in SCALE or k == "OpEx"})
        for label in labels:
            line = diff_row(label, sec.get(label), have.get(label))
            if line:
                print(line)
        print("  (pipeline / backlog / adj. EBITDA: earnings 8-K, not XBRL)")


if __name__ == "__main__":
    main()
