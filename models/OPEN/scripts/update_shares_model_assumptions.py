#!/usr/bin/env python3
"""Refresh Shares tab and re-apply share model formulas (wrapper)."""

from __future__ import annotations

import sys
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(PACK / "scripts"))

from setup_shares_sheet import main

if __name__ == "__main__":
    main()
