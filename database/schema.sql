-- Smart Birdfeeder Database Schema
-- SQLite3
-- Run once to initialise: sqlite3 birdfeeder.db < schema.sql

-- ─── SIGHTINGS ────────────────────────────────────────────────────────────────
-- One row per detected bird visit (visual capture + ID result)
CREATE TABLE IF NOT EXISTS sightings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp           TEXT NOT NULL,              -- ISO8601 e.g. 2026-07-02T15:34:22
    image_path          TEXT NOT NULL,              -- Path to captured JPG
    source              TEXT NOT NULL DEFAULT 'camera',  -- 'camera' or 'haikubox'

    -- Species identification
    common_name         TEXT,                       -- e.g. "House Finch"
    scientific_name     TEXT,                       -- e.g. "Haemorhous mexicanus"
    confidence          REAL,                       -- 0.0–1.0
    taxon_id            INTEGER,                    -- iNaturalist taxon ID

    -- Camera metadata
    lens_position       REAL,
    exposure_us         INTEGER,                    -- microseconds
    analogue_gain       REAL,

    -- Links (populated after ID)
    allaboutbirds_url   TEXT,
    ebird_url           TEXT,

    -- NAS storage (NULL until NAS is available)
    nas_path            TEXT DEFAULT NULL,

    created_at          TEXT DEFAULT (datetime('now'))
);

-- ─── HAIKUBOX DETECTIONS ──────────────────────────────────────────────────────
-- Raw detections pulled from BirdWeather API — merged into sightings separately
CREATE TABLE IF NOT EXISTS haikubox_detections (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    birdweather_id      TEXT UNIQUE,                -- BirdWeather detection ID
    timestamp           TEXT NOT NULL,
    common_name         TEXT,
    scientific_name     TEXT,
    confidence          REAL,
    audio_url           TEXT,                       -- BirdWeather hosted clip URL
    processed           INTEGER DEFAULT 0,          -- 1 = merged into sightings
    created_at          TEXT DEFAULT (datetime('now'))
);

-- ─── SPECIES REGISTRY ─────────────────────────────────────────────────────────
-- Cached species info — populated on first sighting of each species
CREATE TABLE IF NOT EXISTS species (
    taxon_id            INTEGER PRIMARY KEY,
    common_name         TEXT NOT NULL,
    scientific_name     TEXT NOT NULL,
    allaboutbirds_url   TEXT,
    ebird_url           TEXT,
    first_seen          TEXT,
    total_sightings     INTEGER DEFAULT 0,
    last_seen           TEXT
);

-- ─── INDEXES ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_sightings_timestamp   ON sightings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sightings_taxon       ON sightings(taxon_id);
CREATE INDEX IF NOT EXISTS idx_sightings_source      ON sightings(source);
CREATE INDEX IF NOT EXISTS idx_haikubox_timestamp    ON haikubox_detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_haikubox_processed    ON haikubox_detections(processed);
