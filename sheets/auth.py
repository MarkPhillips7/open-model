from pathlib import Path

import gspread
from google.auth.exceptions import RefreshError

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
AUTHORIZED_USER_FILE = CONFIG_DIR / "authorized_user.json"


def get_client() -> gspread.Client:
    """Return an authenticated gspread client using OAuth (desktop app flow)."""
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {CREDENTIALS_FILE}.\n"
            "Download OAuth client credentials from Google Cloud Console "
            "and save them as config/credentials.json. See README.md for steps."
        )

    try:
        return gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(AUTHORIZED_USER_FILE),
        )
    except RefreshError:
        if AUTHORIZED_USER_FILE.exists():
            AUTHORIZED_USER_FILE.unlink()
            print(
                "Saved Google token expired or was revoked; "
                "opening a new sign-in window."
            )
        return gspread.oauth(
            credentials_filename=str(CREDENTIALS_FILE),
            authorized_user_filename=str(AUTHORIZED_USER_FILE),
        )
