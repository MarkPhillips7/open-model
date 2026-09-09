#!/usr/bin/env python3
"""Refresh Shares tab and re-apply share model formulas (wrapper)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.setup_shares_sheet import main

if __name__ == "__main__":
    main()
