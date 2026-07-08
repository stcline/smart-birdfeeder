# Smart Birdfeeder

A Raspberry Pi–powered smart bird feeder with 4K video, AI-based species identification, Haikubox audio detection integration, NAS media storage, and a live web dashboard.

## Overview

This project combines a custom-designed outdoor enclosure (OnShape) with a Raspberry Pi 5 running motion detection and iNaturalist computer vision for visual species identification. Bird audio identifications from a [Haikubox](https://haikubox.com) device are pulled via the [BirdWeather API](https://app.birdweather.com) and merged into a unified SQLite logging database. All captures are stored locally on the Pi SD card until a NAS becomes available. A Flask-based dashboard (planned) will provide live video streaming, clip playback, species statistics, and links to [Cornell Lab of Ornithology](https://www.birds.cornell.edu) resources.

---

## Project Directories

| Directory | Description |
|---|---|
| [`/camera`](./camera) | Camera configuration, motion detection, capture scripts, and species ID |
| [`/haikubox`](./haikubox) | BirdWeather API poller — pulls Haikubox detections and writes to the logging database |
| [`/database`](./database) | SQLite schema and logging utilities |
| [`/dashboard`](./dashboard) | Flask web dashboard — live stream, clip gallery, species stats, Cornell Lab links |
| [`/scripts`](./scripts) | Setup, deployment, and maintenance scripts (NFS mount, service installs, etc.) |
| [`/config`](./config) | Environment variable templates and system configuration |
| [`/enclosure`](./enclosure) | OnShape design files, CAD exports, and enclosure documentation |
| [`/docs`](./docs) | Wiring diagrams, hardware specs, API references, and build notes |
| [`/archive`](./archive) | Retired files and replaced versions — kept for reference |

---

## Hardware

| Component | Model | Notes |
|---|---|---|
| Compute | Raspberry Pi 5 (4GB or 8GB) | Hostname: BirdHouse |
| Camera | Arducam 64MP OwlSight | CSI connection, manual focus LensPosition=12.0 |
| Cooling (SoC) | Official Raspberry Pi Active Cooler | Blower-style, mounts directly on Pi 5 |
| Cooling (enclosure) | Noctua NF-A4x10 5V PWM | GPIO-controlled exhaust fan |
| Audio Detection | Haikubox (existing hardware) | Reports to BirdWeather platform |
| Media Storage | NAS via NFS mount (pending build) | Currently storing to Pi SD card |
| Enclosure | Custom — OnShape design (PETG + TPU gasket, weatherproofed) | |
| Power | Official Raspberry Pi 27W USB-C PSU | Controlled by Shelly 1PM Plus smart switch |
| Smart Switch | Shelly 1PM Plus | Schedules power on/off at sunrise/sunset |

---

## Software Stack

| Layer | Tool |
|---|---|
| Motion detection | Custom picamera2 Python script with polygonal ROI |
| Species identification | [iNaturalist Computer Vision API](https://api.inaturalist.org/v1/docs/) |
| Audio detection | [Haikubox](https://haikubox.com) → [BirdWeather API](https://app.birdweather.com) |
| Data logging | SQLite |
| Dashboard | Python / Flask (planned) |
| Species reference | [Cornell Lab eBird API](https://ebird.org/api/keygen) |
| Media storage | NAS via NFS mount (Pi SD card currently) |
| System service | systemd — auto-starts on power-on |

---

## API Integrations

### iNaturalist Computer Vision
Used for visual species identification of captured images.

- Docs: [iNaturalist API v1](https://api.inaturalist.org/v1/docs/)
- Account: [inaturalist.org](https://www.inaturalist.org) (free)
- Token: [inaturalist.org/users/api_token](https://www.inaturalist.org/users/api_token) — expires every 24 hours
- Set `INAT_API_TOKEN` in `config/.env`

### BirdWeather (Haikubox)
Haikubox devices report detections to the BirdWeather platform. This project polls the BirdWeather API to retrieve detections for the registered station and writes them to the local database.

- API base: `https://app.birdweather.com/api/v1/`
- Key endpoint: `GET /stations/{station_id}/detections`
- Account: [app.birdweather.com](https://app.birdweather.com) (created with Haikubox setup)
- Set `BIRDWEATHER_STATION_ID` and `BIRDWEATHER_TOKEN` in `config/.env`
- See [`/haikubox`](./haikubox) for the polling script and setup instructions

### Cornell Lab eBird API
Used to enrich species records with taxonomy, range maps, and local sighting data.

- Docs: [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59)
- Account: [ebird.org](https://ebird.org) (free) — request API key at [ebird.org/api/keygen](https://ebird.org/api/keygen)
- Set `EBIRD_API_KEY` in `config/.env`
- Species pages: [AllAboutBirds](https://www.allaboutbirds.org/guide/) — linked per detection in the dashboard

---

## API Accounts Needed

| Service | URL | Purpose | Cost |
|---|---|---|---|
| iNaturalist | [inaturalist.org](https://www.inaturalist.org) | Visual species ID | Free |
| BirdWeather | [app.birdweather.com](https://app.birdweather.com) | Haikubox data (already set up with device) | Free |
| eBird / Cornell Lab | [ebird.org](https://ebird.org) | Species data, range maps, taxonomy | Free |

---

## Setup

> Full setup instructions are in [`/docs`](./docs). Quick start below.

```bash
# Clone the repo
git clone https://github.com/stcline/smart-birdfeeder.git
cd smart-birdfeeder

# Install Python dependencies (Raspberry Pi OS Bookworm)
sudo apt install python3-numpy python3-pil python3-requests python3-dotenv -y

# Copy and edit environment config
cp config/.env.example config/.env
nano config/.env   # add your API tokens

# Initialise the database
python3 -c "from database.db import init_db; init_db()"

# Install and enable the capture service
sudo cp camera/bird_capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bird_capture.service
sudo systemctl start bird_capture.service

# Monitor live output
journalctl -u bird_capture.service -f
```

---

## Bird Seed Selection

Choosing the right seed is important for attracting the widest variety of bird species and keeping the feeder healthy. The wrong seed attracts pests, molds quickly, and can discourage the birds you actually want.

### Recommended Seeds for Cypress, CA

| Seed | Birds Attracted | Notes |
|---|---|---|
| **Black oil sunflower seed** | Finches, chickadees, nuthatches, jays, sparrows, towhees | Best all-around choice — highest value seed you can offer. Thin shell makes it accessible to small-beaked birds. Aim for this to be 75%+ of what you offer |
| **Nyjer / thistle** | House finches, lesser goldfinches, pine siskins | Use a tube feeder with small ports. Very popular with SoCal finches year-round |
| **Safflower** | Cardinals, house finches, chickadees | Squirrels dislike it — good choice if squirrels are a problem |
| **Shelled peanuts (unsalted)** | Scrub jays, woodpeckers, nuthatches | High fat content, especially good in winter. Use a peanut feeder or platform |
| **Suet** | Woodpeckers, wrens, warblers | More relevant Oct–Mar in SoCal. Use a caged suet feeder to deter starlings |

### What to Avoid

- **Cheap mixed seed with millet or milo** — attracts house sparrows and pigeons while discouraging the species you want. If a bag is mostly small round seeds, put it back
- **Striped sunflower seed** — birds prefer black oil; striped is harder to open and less nutritious
- **Salted or flavored peanuts** — salt is harmful to birds

### Feeder Hygiene

- Clean the feeder every 1–2 weeks with a mild soap solution, rinse thoroughly, and let it dry completely before refilling
- Check after rain — wet seed molds quickly and can make birds sick
- Store seed in a sealed container in a cool dry location — seed does spoil

### Southern California Specific Notes

- **Lesser goldfinches** are extremely common in Cypress and will swarm a nyjer feeder
- **House finches** are year-round residents and love black oil sunflower
- **California scrub-jays** are regulars and prefer peanuts and suet
- **Anna's hummingbirds** are year-round in SoCal — a separate nectar feeder alongside the seed feeder is worth adding
- Avoid putting out food that attracts crows and pigeons in large numbers as they will dominate the feeder and deter smaller species

### Resources

- [AllAboutBirds — What do birds eat?](https://www.allaboutbirds.org/news/the-best-foods-for-your-bird-feeder/)
- [Cornell Lab — Seeds and Grains poster (PDF)](https://www.birds.cornell.edu/k12/wp-content/uploads/2023/02/SeedsandGrainsPoster.pdf)
- [UC ANR — Feed Wild Birds guide (PDF)](https://ucanr.edu/sites/default/files/2011-10/124156.pdf)
- [eBird — Recent sightings in Cypress, CA](https://ebird.org/hotspots?region=Cypress%2C+California%2C+US)

---

## Dashboard Features (Planned)

- Live 4K RTSP video stream (HLS in browser)
- Motion-triggered capture gallery with species labels
- Species detection log — visual (iNaturalist) and audio (Haikubox) merged
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

- [iNaturalist Computer Vision API](https://api.inaturalist.org/v1/docs/)
- [BirdWeather API](https://app.birdweather.com)
- [Cornell Lab of Ornithology](https://www.birds.cornell.edu)
- [eBird API 2.0](https://documenter.getpostman.com/view/664302/S1ENwy59)
- [AllAboutBirds](https://www.allaboutbirds.org)
- [Haikubox](https://haikubox.com)
- [Arducam 64MP OwlSight](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/64MP-OV64A40/)
- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [OnShape](https://www.onshape.com)
- [Shelly 1PM Plus](https://www.shelly.com/en-us/products/shop/shelly-plus-1-pm)
