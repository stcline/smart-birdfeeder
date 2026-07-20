"""
db.py
-----
Database access layer for the Smart Birdfeeder project.
Handles SQLite reads and writes for sightings, species registry,
and Haikubox detections.
"""

import sqlite3
import logging
import os
from datetime import datetime

log = logging.getLogger(__name__)

# Default DB path — override via DB_PATH env var
DB_PATH = os.environ.get("DB_PATH", "/home/steve/birdfeeder/birdfeeder.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    """Return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialise the database from schema.sql if tables don't exist."""
    with get_connection() as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
    log.info(f"Database initialised at {DB_PATH}")


def log_sighting(
    timestamp: str,
    image_path: str,
    common_name: str = None,
    scientific_name: str = None,
    confidence: float = None,
    taxon_id: int = None,
    lens_position: float = None,
    exposure_us: int = None,
    analogue_gain: float = None,
    source: str = "camera",
) -> int:
    """
    Insert a new sighting record. Returns the new row ID.
    Image path stored as local SD path initially; NAS path updated later.
    """
    allaboutbirds_url = None
    ebird_url = None

    if common_name:
        # Build Cornell Lab links from common name
        slug = common_name.lower().replace(" ", "_").replace("'", "")
        allaboutbirds_url = f"https://www.allaboutbirds.org/guide/{slug}"
        ebird_url = f"https://ebird.org/species/{slug}"

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO sightings (
                timestamp, image_path, source,
                common_name, scientific_name, confidence, taxon_id,
                lens_position, exposure_us, analogue_gain,
                allaboutbirds_url, ebird_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp, image_path, source,
                common_name, scientific_name, confidence, taxon_id,
                lens_position, exposure_us, analogue_gain,
                allaboutbirds_url, ebird_url,
            )
        )
        row_id = cursor.lastrowid

    # Update species registry
    if taxon_id and common_name:
        _update_species_registry(
            taxon_id, common_name, scientific_name,
            allaboutbirds_url, ebird_url, timestamp
        )

    conf_str = f"{confidence:.2f}" if confidence is not None else "N/A"
    log.info(
        f"Sighting logged — {common_name or 'Unknown'} "
        f"(confidence={conf_str}) "
        f"[row {row_id}]"
    )
    return row_id


def _update_species_registry(
    taxon_id, common_name, scientific_name,
    allaboutbirds_url, ebird_url, timestamp
):
    """Upsert species registry entry and increment sighting count."""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT taxon_id FROM species WHERE taxon_id = ?", (taxon_id,)
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE species
                SET total_sightings = total_sightings + 1,
                    last_seen = ?
                WHERE taxon_id = ?
                """,
                (timestamp, taxon_id)
            )
        else:
            conn.execute(
                """
                INSERT INTO species (
                    taxon_id, common_name, scientific_name,
                    allaboutbirds_url, ebird_url,
                    first_seen, last_seen, total_sightings
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    taxon_id, common_name, scientific_name,
                    allaboutbirds_url, ebird_url,
                    timestamp, timestamp
                )
            )
            log.info(f"New species added to registry: {common_name}")


def update_nas_path(row_id: int, nas_path: str):
    """Update the NAS path for a sighting once the NAS is available."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE sightings SET nas_path = ? WHERE id = ?",
            (nas_path, row_id)
        )


def get_recent_sightings(limit: int = 50):
    """Return the most recent sightings for the dashboard."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM sightings
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()


def get_species_summary():
    """Return all species with sighting counts for dashboard stats."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT * FROM species
            ORDER BY total_sightings DESC
            """
        ).fetchall()
