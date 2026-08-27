#!/usr/bin/env python3
"""Run once to complete OAuth sign-in. Opens a browser window."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sheets.auth import AUTHORIZED_USER_FILE, CREDENTIALS_FILE, get_client


def main() -> None:
    print("Google Sheets OAuth setup")
    print("=" * 40)

    if not CREDENTIALS_FILE.exists():
        print(f"\nMissing: {CREDENTIALS_FILE}")
        print("Download OAuth credentials from Google Cloud Console first.")
        print("See README.md for step-by-step instructions.")
        sys.exit(1)

    print(f"\nCredentials: {CREDENTIALS_FILE}")
    print("A browser window will open for Google sign-in.\n")

    client = get_client()

    if AUTHORIZED_USER_FILE.exists():
        print(f"Authorized user saved to: {AUTHORIZED_USER_FILE}")
    else:
        print("Authorization complete.")

    spreadsheets = client.list_spreadsheet_files()[:5]
    print(f"\nConnected as Google account with access to {len(spreadsheets)} recent spreadsheet(s).")
    if spreadsheets:
        print("\nRecent spreadsheets:")
        for sheet in spreadsheets[:5]:
            print(f"  - {sheet['name']}")


if __name__ == "__main__":
    main()
