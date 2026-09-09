"""Ticker registry: settings.json → spreadsheet IDs, pack modules, snapshot paths.

Ticker keys are filesystem-safe tokens (``OPEN``, ``EOSE``, ``CSIQ``, ``BTCUSD``).
Pack modules live under ``models/{TICKER}/`` and are loaded by path so keys like
``BRK.B`` do not need to be valid Python package names.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
MODELS_DIR = REPO_ROOT / "models"
ENV_TICKER = "OPEN_MODEL_TICKER"

TICKER_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_SHEET_ID_IN_URL = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


def extract_spreadsheet_id(value: str) -> str:
    """Accept a raw ID or a full Google Sheets URL."""
    value = value.strip()
    match = _SHEET_ID_IN_URL.search(value)
    return match.group(1) if match else value


def load_settings() -> dict[str, Any]:
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {SETTINGS_FILE}.\n"
            "Copy config/settings.example.json to config/settings.json "
            "and set each ticker's spreadsheet_id."
        )
    raw = json.loads(SETTINGS_FILE.read_text())
    return _normalize_settings(raw)


def _normalize_settings(raw: dict[str, Any]) -> dict[str, Any]:
    """Accept legacy ``{spreadsheet_id: ...}`` as ticker OPEN."""
    if raw.get("tickers"):
        return raw
    spreadsheet_id = str(raw.get("spreadsheet_id", "")).strip()
    if spreadsheet_id and spreadsheet_id != "paste-your-spreadsheet-id-here":
        return {
            "default_ticker": "OPEN",
            "tickers": {
                "OPEN": {
                    "name": "Opendoor Technologies",
                    "spreadsheet_id": spreadsheet_id,
                    "price_symbol": "OPEN",
                }
            },
        }
    return raw


def list_tickers() -> list[str]:
    settings = load_settings()
    return sorted((settings.get("tickers") or {}).keys())


def resolve_ticker(ticker: str | None = None) -> str:
    """Resolve ticker from argument, ``OPEN_MODEL_TICKER``, or settings.default_ticker."""
    if ticker and ticker.strip():
        return ticker.strip()
    env = os.environ.get(ENV_TICKER, "").strip()
    if env:
        return env
    settings = load_settings()
    default = str(settings.get("default_ticker", "")).strip()
    if default:
        return default
    tickers = settings.get("tickers") or {}
    if len(tickers) == 1:
        return next(iter(tickers))
    raise ValueError(
        "Pass --ticker, set OPEN_MODEL_TICKER, or settings.default_ticker "
        f"in {SETTINGS_FILE}."
    )


def get_ticker_config(ticker: str | None = None) -> dict[str, Any]:
    key = resolve_ticker(ticker)
    settings = load_settings()
    tickers = settings.get("tickers") or {}
    if key not in tickers:
        known = ", ".join(sorted(tickers)) or "(none)"
        raise KeyError(f"Ticker {key!r} not in {SETTINGS_FILE}. Known: {known}")
    cfg = tickers[key]
    if not isinstance(cfg, dict):
        raise TypeError(f"tickers.{key} must be an object")
    return cfg


def spreadsheet_id_for(ticker: str | None = None) -> str:
    cfg = get_ticker_config(ticker)
    spreadsheet_id = str(cfg.get("spreadsheet_id", "")).strip()
    if not spreadsheet_id or spreadsheet_id == "paste-or-url":
        key = resolve_ticker(ticker)
        raise ValueError(
            f"Set tickers.{key}.spreadsheet_id in {SETTINGS_FILE} "
            "(paste the ID or full Google Sheets URL)."
        )
    return extract_spreadsheet_id(spreadsheet_id)


def price_symbol_for(ticker: str | None = None) -> str:
    cfg = get_ticker_config(ticker)
    symbol = str(cfg.get("price_symbol", "")).strip()
    return symbol or resolve_ticker(ticker)


def ticker_name(ticker: str | None = None) -> str:
    cfg = get_ticker_config(ticker)
    name = str(cfg.get("name", "")).strip()
    return name or resolve_ticker(ticker)


def pack_dir(ticker: str | None = None) -> Path:
    key = resolve_ticker(ticker)
    path = MODELS_DIR / key
    if not path.is_dir():
        raise FileNotFoundError(f"No model pack at {path}")
    return path


def snapshot_path(ticker: str | None = None) -> Path:
    return pack_dir(ticker) / "snapshot.json"


def changelog_path(ticker: str | None = None) -> Path:
    return pack_dir(ticker) / "CHANGELOG.md"


def pack_script(ticker: str, name: str) -> Path:
    """Path to ``models/{TICKER}/scripts/{name}``."""
    return pack_dir(ticker) / "scripts" / name


def validate_ticker_key(ticker: str) -> str:
    key = ticker.strip()
    if not TICKER_KEY_RE.match(key):
        raise ValueError(
            f"Invalid ticker key {ticker!r}. Use letters, digits, '.', '_', or '-' "
            "(e.g. OPEN, EOSE, BTCUSD)."
        )
    return key


def parse_ticker_argv(argv: list[str] | None = None) -> tuple[str | None, list[str]]:
    """Extract ``--ticker VALUE`` or ``--ticker=VALUE``; return (ticker, remaining)."""
    args = list(sys.argv[1:] if argv is None else argv)
    ticker: str | None = None
    remaining: list[str] = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--ticker" and i + 1 < len(args):
            ticker = args[i + 1]
            i += 2
            continue
        if arg.startswith("--ticker="):
            ticker = arg.split("=", 1)[1]
            i += 1
            continue
        remaining.append(arg)
        i += 1
    return ticker, remaining


def _package_name(ticker: str) -> str:
    if ticker.isidentifier():
        return f"models.{ticker}"
    safe = re.sub(r"[^A-Za-z0-9_]", "_", ticker)
    return f"_open_model_pack_{safe}"


def _ensure_pack_package(ticker: str) -> str:
    """Register ``models/{ticker}/`` as a package and return its import name."""
    key = resolve_ticker(ticker)
    directory = MODELS_DIR / key
    if not directory.is_dir():
        raise FileNotFoundError(f"No model pack at {directory}")

    pkg_name = _package_name(key)
    if pkg_name in sys.modules:
        return pkg_name

    if key.isidentifier():
        models_pkg = MODELS_DIR / "__init__.py"
        if not models_pkg.exists():
            # Namespace fallback if models/ is not a package yet.
            pass
        try:
            importlib.import_module(f"models.{key}")
            return pkg_name
        except ImportError:
            pass

    init_py = directory / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        pkg_name,
        init_py if init_py.is_file() else None,
        submodule_search_locations=[str(directory)],
    )
    if spec is None:
        module = ModuleType(pkg_name)
        module.__path__ = [str(directory)]  # type: ignore[attr-defined]
        sys.modules[pkg_name] = module
        return pkg_name

    module = importlib.util.module_from_spec(spec)
    module.__path__ = [str(directory)]  # type: ignore[attr-defined]
    sys.modules[pkg_name] = module
    if spec.loader is not None and init_py.is_file():
        spec.loader.exec_module(module)
    return pkg_name


def load_formula_module(ticker: str) -> ModuleType:
    """Load weekly or quarterly model-formula module for *ticker*."""
    key = resolve_ticker(ticker)
    directory = pack_dir(key)
    if (directory / "weekly_model_formulas.py").is_file():
        return load_pack_module(key, "weekly_model_formulas")
    if (directory / "quarterly_model_formulas.py").is_file():
        return load_pack_module(key, "quarterly_model_formulas")
    raise FileNotFoundError(
        f"No weekly_model_formulas.py or quarterly_model_formulas.py in {directory}"
    )


def load_pack_module(ticker: str, module_name: str) -> ModuleType:
    """Load ``models/{ticker}/{module_name}.py`` as a module."""
    key = resolve_ticker(ticker)
    directory = pack_dir(key)
    file_path = directory / f"{module_name}.py"
    if not file_path.is_file():
        raise FileNotFoundError(f"Pack module not found: {file_path}")

    pkg_name = _ensure_pack_package(key)
    full_name = f"{pkg_name}.{module_name}"
    if full_name in sys.modules:
        return sys.modules[full_name]

    if key.isidentifier():
        try:
            return importlib.import_module(full_name)
        except ImportError:
            pass

    spec = importlib.util.spec_from_file_location(full_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module
