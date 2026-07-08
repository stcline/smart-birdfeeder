"""
identify.py
-----------
Bird species identification via the iNaturalist Computer Vision API.
Called immediately after each capture in bird_capture.py.

API docs: https://api.inaturalist.org/v1/docs/
Auth:     JWT token from https://www.inaturalist.org/users/api_token
          Token expires every 24 hours — script auto-refreshes via env var.
"""

import os
import logging
import requests
from dotenv import load_dotenv

log = logging.getLogger(__name__)

# Resolve .env path relative to this file — works regardless of working directory
_ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", ".env")

INAT_API_BASE = "https://api.inaturalist.org/v1"

# Location hint — improves ID accuracy by narrowing to local species
# Cypress, CA coordinates
LOCATION_LAT = 33.8169
LOCATION_LNG = -118.0375

# Minimum vision_score (0.0–1.0) to accept a result.
# 0.50 = iNaturalist needs to be at least 50% confident it's this species.
# vision_score is the per-image ML probability; combined_score is a raw
# ranking score that can exceed 1.0 and should NOT be used as a threshold.
MIN_CONFIDENCE = 0.50


def get_token() -> str:
    """
    Read iNaturalist JWT token from .env file directly.
    Reloads on every call so token updates without restarting the service.
    Set INAT_API_TOKEN in your config/.env file.
    """
    load_dotenv(_ENV_PATH, override=True)
    token = os.environ.get("INAT_API_TOKEN", "")
    if not token:
        raise EnvironmentError(
            "INAT_API_TOKEN not set. Add it to config/.env"
        )
    return token


def identify_bird(image_path: str, min_confidence: float = MIN_CONFIDENCE) -> dict | None:
    """
    Submit a captured image to the iNaturalist Computer Vision API.
    Only returns a result if:
      1. The top result is classified as a bird (iconic_taxon_name == "Aves")
      2. The vision_score (0.0–1.0) is at or above min_confidence

    Args:
        image_path:      Absolute path to the captured JPEG
        min_confidence:  Minimum vision_score to accept (0.0–1.0)
                         Default 0.50 — require 50% confidence

    Returns:
        {
            "common_name":     str,
            "scientific_name": str,
            "confidence":      float,   # vision_score, 0.0–1.0
            "taxon_id":        int,
        }
        or None if no bird result above min_confidence
    """
    try:
        token = get_token()

        with open(image_path, "rb") as img_file:
            response = requests.post(
                f"{INAT_API_BASE}/computervision/score_image",
                headers={"Authorization": f"Bearer {token}"},
                files={"image": img_file},
                data={
                    "lat": LOCATION_LAT,
                    "lng": LOCATION_LNG,
                },
                timeout=30
            )

        if response.status_code == 401:
            log.error("iNaturalist token rejected (401) — check INAT_API_TOKEN in config/.env")
            return None

        if response.status_code != 200:
            log.error(f"iNaturalist API error {response.status_code}: {response.text[:200]}")
            return None

        results = response.json().get("results", [])

        if not results:
            log.info("iNaturalist returned no results for this image")
            return None

        top = results[0]
        taxon = top.get("taxon", {})

        # ── Bird-only filter ────────────────────────────────────────────────
        # iconic_taxon_name == "Aves" means it's a bird.
        # Without this, insects, plants, fungi, etc. can sneak through.
        iconic = taxon.get("iconic_taxon_name")
        if iconic != "Aves":
            log.info(
                f"Non-bird result filtered out: {taxon.get('name', 'Unknown')} "
                f"(iconic_taxon_name={iconic!r})"
            )
            return None

        # ── Use vision_score (0.0–1.0), not combined_score ─────────────────
        # combined_score is a raw ranking number that can exceed 1.0 and
        # is NOT suitable as a confidence percentage threshold.
        confidence = top.get("vision_score", 0)

        common_name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
        scientific_name = taxon.get("name", "Unknown")
        taxon_id = taxon.get("id")

        if confidence < min_confidence:
            log.info(
                f"Low confidence bird: {common_name} ({confidence:.1%}) "
                f"— below threshold {min_confidence:.0%}, skipping"
            )
            return None

        result = {
            "common_name":     common_name,
            "scientific_name": scientific_name,
            "confidence":      confidence,
            "taxon_id":        taxon_id,
        }

        log.info(
            f"Bird identified: {common_name} ({scientific_name}) "
            f"— confidence {confidence:.1%}"
        )

        # Log runner-up for reference (if also a bird)
        if len(results) > 1:
            runner = results[1]
            runner_taxon = runner.get("taxon", {})
            runner_name = runner_taxon.get("preferred_common_name", runner_taxon.get("name", "?"))
            runner_conf = runner.get("vision_score", 0)
            runner_iconic = runner_taxon.get("iconic_taxon_name")
            if runner_iconic == "Aves":
                log.info(f"  Runner-up: {runner_name} ({runner_conf:.1%})")

        return result

    except requests.exceptions.Timeout:
        log.error("iNaturalist API timed out after 30s")
        return None
    except requests.exceptions.ConnectionError:
        log.error("iNaturalist API unreachable — check Wi-Fi connection")
        return None
    except Exception as e:
        log.error(f"Unexpected error during bird ID: {e}")
        return None
