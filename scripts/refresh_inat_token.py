"""
refresh_inat_token.py
---------------------
Automatically refreshes the iNaturalist JWT token and writes it
to config/.env. Run daily via cron to prevent token expiry.

Two-step process:
  1. POST to /oauth/token with username/password + app credentials
     → returns OAuth access token
  2. GET /users/api_token with OAuth token in header
     → returns fresh JWT

Prerequisites:
  Register a free iNaturalist OAuth app at:
  https://www.inaturalist.org/oauth/applications/new
    - Name: smart-birdfeeder (or any name)
    - Confidential: checked
    - Redirect URI: https://localhost (placeholder is fine)
  Save the App ID and Secret to config/.env

Required .env entries:
  INAT_USERNAME=your_inaturalist_username
  INAT_PASSWORD=your_inaturalist_password
  INAT_APP_ID=your_oauth_app_id
  INAT_APP_SECRET=your_oauth_app_secret

This script updates INAT_API_TOKEN in config/.env automatically.
The bird_capture.py service reloads the token on every API call
so no service restart is needed after this script runs.
"""

import os
import re
import sys
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv

# ─── PATHS ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH   = SCRIPT_DIR.parent / "config" / ".env"
LOG_PATH   = Path("/home/steve/birdfeeder/token_refresh.log")

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(LOG_PATH))
    ]
)
log = logging.getLogger(__name__)

INAT_BASE = "https://www.inaturalist.org"


def load_credentials():
    """Load credentials from .env file."""
    load_dotenv(ENV_PATH, override=True)
    required = ["INAT_USERNAME", "INAT_PASSWORD", "INAT_APP_ID", "INAT_APP_SECRET"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        log.error(f"Missing required .env entries: {', '.join(missing)}")
        log.error("See script header for setup instructions.")
        sys.exit(1)
    return {k: os.environ[k] for k in required}


def get_oauth_token(creds: dict) -> str:
    """Step 1 — Exchange username/password for OAuth access token."""
    response = requests.post(
        f"{INAT_BASE}/oauth/token",
        json={
            "client_id":     creds["INAT_APP_ID"],
            "client_secret": creds["INAT_APP_SECRET"],
            "grant_type":    "password",
            "username":      creds["INAT_USERNAME"],
            "password":      creds["INAT_PASSWORD"],
        },
        timeout=30
    )
    if response.status_code != 200:
        log.error(f"OAuth token request failed ({response.status_code}): {response.text[:200]}")
        sys.exit(1)

    token = response.json().get("access_token")
    if not token:
        log.error("No access_token in OAuth response")
        sys.exit(1)

    log.info("OAuth access token obtained")
    return token


def get_jwt(oauth_token: str) -> str:
    """Step 2 — Exchange OAuth token for iNaturalist JWT."""
    response = requests.get(
        f"{INAT_BASE}/users/api_token",
        headers={"Authorization": f"Bearer {oauth_token}"},
        timeout=30
    )
    if response.status_code != 200:
        log.error(f"JWT request failed ({response.status_code}): {response.text[:200]}")
        sys.exit(1)

    jwt = response.json().get("api_token")
    if not jwt:
        log.error("No api_token in JWT response")
        sys.exit(1)

    log.info("JWT obtained successfully")
    return jwt


def update_env_token(jwt: str):
    """Write the new JWT back to config/.env, replacing the existing value."""
    env_text = ENV_PATH.read_text()

    if "INAT_API_TOKEN=" in env_text:
        # Replace existing token line
        env_text = re.sub(
            r"^INAT_API_TOKEN=.*$",
            f"INAT_API_TOKEN={jwt}",
            env_text,
            flags=re.MULTILINE
        )
    else:
        # Append if not present
        env_text += f"\nINAT_API_TOKEN={jwt}\n"

    ENV_PATH.write_text(env_text)
    log.info(f"INAT_API_TOKEN updated in {ENV_PATH}")


def main():
    log.info("=== iNaturalist Token Refresh Starting ===")
    creds = load_credentials()
    oauth_token = get_oauth_token(creds)
    jwt = get_jwt(oauth_token)
    update_env_token(jwt)
    log.info("=== Token Refresh Complete ===")


if __name__ == "__main__":
    main()
