# Smart Birdfeeder

A Raspberry Pi–powered smart bird feeder with 4K video, AI-based species identification, Haikubox audio detection integration, NAS media storage, and a live web dashboard.

## Overview

This project combines a custom-designed outdoor enclosure (Fusion 360) with a Raspberry Pi 5 running Frigate NVR for visual species detection. Bird audio identifications from a [Haikubox](https://haikubox.com) device are pulled via the [BirdWeather API](https://app.birdweather.com) and merged into a unified logging database. All video clips and snapshots are stored on a local NAS. A Flask-based dashboard provides live video streaming, clip playback, species statistics, and links to [Cornell Lab of Ornithology](https://www.birds.cornell.edu) resources.

---

## Project Directories

| Directory | Description |
|---|---|
| [`/camera`](./camera) | Camera configuration, stream setup, and capture scripts for the Pi Camera Module |
| [`/frigate`](./frigate) | Frigate NVR configuration files for motion detection and species classification |
| [`/haikubox`](./haikubox) | BirdWeather API poller — pulls Haikubox detections and writes to the logging database |
| [`/database`](./database) | SQLite schema, migration scripts, and logging utilities |
| [`/dashboard`](./dashboard) | Flask web dashboard — live stream, clip gallery, species stats, Cornell Lab links |
| [`/scripts`](./scripts) | Setup, deployment, and maintenance scripts (NFS mount, service installs, etc.) |
| [`/config`](./config) | System configuration templates (Frigate YAML, NFS fstab entries, environment variables) |
| [`/enclosure`](./enclosure) | Fusion 360 design files, CAD exports, and enclosure documentation |
| [`/docs`](./docs) | Wiring diagrams, hardware specs, API references, and build notes |
| [`/archive`](./archive) | Retired files and replaced versions — kept for reference |

---

## Hardware

| Component | Model |
|---|---|
| Compute | Raspberry Pi 5 (4GB or 8GB) |
| Camera | Pi Camera Module 3 (standard) or Arducam 64MP OwlSight |
| Cooling | Raspberry Pi Active Cooler (blower) |
| Audio Detection | Haikubox (existing hardware) |
| Media Storage | NAS via NFS mount |
| Enclosure | Custom — Fusion 360 design (weatherproofed) |
| Power | Weatherproof 5V supply or PoE HAT |

---

## Software Stack

| Layer | Tool |
|---|---|
| Video capture & detection | [Frigate NVR](https://frigate.video) |
| Species classification | Frigate built-in (900+ species sublabeling) |
| Audio detection | [Haikubox](https://haikubox.com) → [BirdWeather API](https://app.birdweather.com) |
| Data logging | SQLite |
| Dashboard | Python / Flask |
| Species reference | [Cornell Lab eBird API](https://ebird.org/api/keygen) |
| Media storage | NAS (NFS mount) |

---

## API Integrations

### BirdWeather (Haikubox)
Haikubox devices report detections to the BirdWeather platform. This project polls the BirdWeather API to retrieve detections for the registered station and writes them to the local database.

- API base: `https://app.birdweather.com/api/v1/`
- Key endpoint: `GET /stations/{station_id}/detections`
- See [`/haikubox`](./haikubox) for the polling script and setup instructions

### Cornell Lab eBird API
Used to enrich species records with taxonomy, range maps, and local sighting data.

- Docs: [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59)
- Requires a free API key from your [eBird account](https://ebird.org/api/keygen)
- Species pages: [AllAboutBirds](https://www.allaboutbirds.org/guide/) — linked per detection in the dashboard

---

## Setup

> Full setup instructions are in [`/docs`](./docs). Quick start below.

```bash
# Clone the repo
git clone https://github.com/<your-username>/smart-birdfeeder.git
cd smart-birdfeeder

# Install Python dependencies
pip install -r requirements.txt

# Copy and edit environment config
cp config/.env.example config/.env

# Mount NAS share (see /scripts/mount_nas.sh)
bash scripts/mount_nas.sh

# Start Frigate (see /frigate/README.md)
# Start dashboard
python dashboard/app.py
```

---

## Dashboard Features

- Live 4K RTSP video stream (HLS in browser)
- Motion-triggered clip gallery with species labels
- Species detection log — visual (Frigate) and audio (Haikubox) merged
- Visit statistics by species, hour, and day
- Per-species links to [AllAboutBirds](https://www.allaboutbirds.org) and [eBird](https://ebird.org)
- Raspberry Pi system health (CPU temp, uptime)

---

## Archive

The [`/archive`](./archive) directory holds any files that have been superseded by updated versions. Files are moved here rather than deleted to preserve project history outside of git diffs.

---

## License

MIT

---

## References

- [Frigate NVR](https://frigate.video)
- [BirdWeather API](https://app.birdweather.com)
- [Cornell Lab of Ornithology](https://www.birds.cornell.edu)
- [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59)
- [AllAboutBirds](https://www.allaboutbirds.org)
- [Haikubox](https://haikubox.com)
- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Arducam 64MP OwlSight](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/64MP-OV64A40/)
