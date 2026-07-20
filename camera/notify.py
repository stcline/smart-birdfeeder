"""
notify.py
---------
Pushover push notification helper for the Smart Birdfeeder.

Sends a phone notification when a bird is successfully identified,
optionally attaching the captured image.

Pushover setup:
  1. Create account at https://pushover.net
  2. Note your User Key from the dashboard
  3. Create an application at https://pushover.net/apps/build
  4. Note your App Token (API Token)
  5. Add both to config/.env:
       PUSHOVER_USER_KEY=your_user_key
       PUSHOVER_APP_TOKEN=your_app_token
  6. Download the Pushover app on your phone ($5 one-time)

If either key is missing or blank, notifications are silently skipped
so the capture service keeps running without error.
"""

import os
import logging
import requests
from dotenv import load_dotenv

log = logging.getLogger(__name__)

_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", ".env")
PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"

# Maximum image size Pushover accepts (2.5 MB)
MAX_IMAGE_BYTES = 2_500_000


def _get_credentials() -> tuple[str, str] | tuple[None, None]:
    """Load Pushover credentials from .env. Returns (user_key, app_token) or (None, None)."""
    load_dotenv(_ENV_PATH, override=True)
    user_key = os.environ.get("PUSHOVER_USER_KEY", "").strip()
    app_token = os.environ.get("PUSHOVER_APP_TOKEN", "").strip()
    if not user_key or not app_token:
        return None, None
    return user_key, app_token


def send_bird_alert(
    common_name: str,
    scientific_name: str,
    confidence: float,
    image_path: str = None,
) -> bool:
    """
    Send a Pushover notification for a confirmed bird sighting.

    Args:
        common_name:     e.g. "Black Phoebe"
        scientific_name: e.g. "Sayornis nigricans"
        confidence:      vision_score 0.0–1.0
        image_path:      path to captured JPEG (attached if under 2.5 MB)

    Returns:
        True if notification sent successfully, False otherwise.
    """
    user_key, app_token = _get_credentials()
    if not user_key:
        # Credentials not configured — skip silently
        return False

    title = f"Bird spotted: {common_name}"
    message = (
        f"{common_name} ({scientific_name})\n"
        f"Score: {confidence:.2f}"
    )

    data = {
        "token":   app_token,
        "user":    user_key,
        "title":   title,
        "message": message,
        "sound":   "magic",   # pleasant chime — change to "none" to silence
    }

    files = None
    if image_path and os.path.isfile(image_path):
        size = os.path.getsize(image_path)
        if size <= MAX_IMAGE_BYTES:
            files = {"attachment": (os.path.basename(image_path), open(image_path, "rb"), "image/jpeg")}
        else:
            log.warning(f"Image too large for Pushover ({size / 1e6:.1f} MB) — sending without photo")

    try:
        response = requests.post(
            PUSHOVER_API_URL,
            data=data,
            files=files,
            timeout=15,
        )
        if files:
            files["attachment"][1].close()

        if response.status_code == 200 and response.json().get("status") == 1:
            log.info(f"Pushover notification sent: {common_name} ({confidence:.0%})")
            return True
        else:
            log.error(f"Pushover error {response.status_code}: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        log.error("Pushover notification timed out")
        return False
    except Exception as e:
        log.error(f"Pushover notification failed: {e}")
        return False
