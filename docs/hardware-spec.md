# Smart Birdfeeder — Hardware Specification

This document captures all hardware decisions. Update when components change; move superseded versions to `/archive`.

---

## Compute

| Component | Model | Notes |
|---|---|---|
| Single-board computer | Raspberry Pi 5 (4GB or 8GB) | Hostname: BirdHouse; runs motion detection, iNaturalist ID, BirdWeather poller, and Flask dashboard |

---

## Power

| Component | Model | Notes |
|---|---|---|
| Power supply | Official Raspberry Pi 27W USB-C PSU | 5.1V / 5A; plugs into outdoor GFCI outlet via female spade terminals on plug prongs connected to hot/neutral wiring inside weatherproof junction box |
| Smart switch | Shelly 1PM Plus | Controls power to the outlet; scheduled on/off at sunrise/sunset via Shelly app — Pi powers down at night since no night vision |
| Cable entry | IP68 M20 cable gland | USB-C cable passes through gland on enclosure bottom or side face |

> **Note:** PoE was considered but not used — no Ethernet run is available at the installation location. Network connectivity is via the Pi 5's built-in Wi-Fi.

> **Note:** GPIO power path via IRM-30-5 AC-DC converter was evaluated but replaced with the official USB-C PSU for cleaner power delivery and proper Pi 5 voltage negotiation. IRM-30-5 archived.

---

## Cooling

Two-layer cooling strategy for outdoor enclosure use (Cypress, CA — high ambient summer temps).

| Component | Model | Purpose | Control |
|---|---|---|---|
| SoC cooler | [Official Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/) | Cools Pi 5 SoC directly; mounts directly on Pi 5 | Pi firmware — automatic PWM |
| Enclosure exhaust fan | [Noctua NF-A4x10 5V PWM](https://www.amazon.com/Noctua-NF-A4x10-5V-PWM-Premium/dp/B07DXS86G7/) (ASIN: B07DXS86G7) | Exhausts hot air from electronics compartment through louvered vent | GPIO PWM script — temperature-triggered (~65°C on, 100% at 75°C+) |

### Fan Wiring (GPIO Header)

| Fan Wire | Color | GPIO Pin | Function |
|---|---|---|---|
| Ground | Black | Pin 6 | GND |
| Power | Yellow | Pin 4 | 5V |
| PWM | Blue | Pin 33 (GPIO13) | Hardware PWM speed control |
| Tach | Green | Pin 35 (GPIO19) | Optional — RPM monitoring |

A BSS138 logic level shifter (3.3V → 5V) is recommended between GPIO PWM pin and fan PWM wire for full speed ramping. Alternatively wire for on/off control only.

### Enclosure Cooling Design Notes
- Electronics compartment physically separated from birdseed compartment by internal partition
- Noctua fan mounts in 40mm cutout in electronics compartment wall (4× M3 holes on 32mm bolt circle)
- Fan exhausts outward; intake is filtered vent on opposite face (bottom preferred for rain protection)
- Vents covered with 0.45µm hydrophobic PTFE membrane held by printed PETG retaining rings
- Light-colored exterior to minimize solar gain
- Pi SoC temperature monitored via `vcgencmd measure_temp` and surfaced in dashboard

### Stack Height
Pi 5 + Official Active Cooler stacked height should be confirmed from Raspberry Pi documentation before finalizing electronics compartment height in OnShape.

---

## Camera

| Status | Model | Focal Length | FoV (H) | Resolution | Notes |
|---|---|---|---|---|---|
| **Selected** | **Arducam 64MP OwlSight** | **6.65mm** | **68°** | **64MP** | Manual focus; LensPosition=12.0 for feeder distance ~10–13cm; CSI connection |
| Evaluated | Pi Camera Module 3 (standard) | 4.74mm | 66° | 12MP (Sony IMX708) | Good low-light; lower resolution |
| Evaluated | Pi Camera V2, Pi AI Camera | Similar FoV | ~66° | 12MP | Not selected |
| Avoid | Pi Camera Module 3 Wide | 2.75mm | 102° | 12MP | Too wide for close feeder distance |

**Capture resolution in use:** 4056×3040 (balanced quality vs. file size)
**dtoverlay:** `dtoverlay=ov64a40,link-frequency=360000000` with `camera_auto_detect=0`

---

## Enclosure

| Item | Detail |
|---|---|
| CAD software | [OnShape](https://www.onshape.com) (cloud-based, free for public projects) |
| Body material | PETG — UV resistant, ~80°C heat deflection, easy to print |
| Gasket material | Shore 95A TPU — compresses to seal against PETG mating surface |
| Fasteners | Stainless M3/M4 screws throughout — corrosion resistant |
| Lid seal | Compression fit with captured TPU gasket in routed groove; 4–6 stainless screws around perimeter |
| Cable entry | IP68 M20 cable gland on bottom or side face — never top |
| Vent membranes | 0.45µm hydrophobic PTFE membrane with PETG snap-fit retaining rings |
| Fan cutout | 40mm circular, 32mm bolt circle for M3 mounting screws |

Design files stored in [`/enclosure`](../enclosure).

---

## Bird Audio Detection

| Component | Model | Notes |
|---|---|---|
| Audio detector | [Haikubox](https://haikubox.com) | Existing hardware — kept in place; reports to BirdWeather platform |
| API integration | [BirdWeather API](https://app.birdweather.com/api/v1/) | Polled by Python script in `/haikubox`; detections merged into local SQLite database |

No additional audio hardware is planned. The Haikubox handles all audio-based species identification.

---

## Media Storage

| Component | Notes |
|---|---|
| Current | Pi SD card — `/home/steve/birdfeeder/captures/` |
| Planned | NAS via NFS mount — separate NAS build in progress |
| Protocol | NFSv3 or NFSv4 |
| NAS directory structure | `/birdfeeder/clips/` and `/birdfeeder/snapshots/` |
| Retention policy | Clips: 7 days auto-delete; snapshots: 30 days; `/saved/`: never deleted |
| Transition | Update `SAVE_DIR` in `config/.env` and `bird_capture.py` when NAS is ready |

---

## Optional Upgrades

| Component | Purpose | Notes |
|---|---|---|
| Google Coral USB Accelerator | Offloads object detection from CPU | ~$60–80; USB 3.0 plug-and-play; add if CPU temps become problematic |

---

## Shopping List

| Item | Source | Approx. Cost | Status |
|---|---|---|---|
| Raspberry Pi 5 (4GB or 8GB) | raspberrypi.com / Amazon | $60–80 | Purchased |
| Official Pi 5 Active Cooler | raspberrypi.com / Amazon | $5 | Purchased |
| Noctua NF-A4x10 5V PWM (ASIN: B07DXS86G7) | [Amazon](https://www.amazon.com/dp/B07DXS86G7) | $16 | Purchased |
| Arducam 64MP OwlSight | Amazon | $50 | Purchased |
| Official Raspberry Pi 27W USB-C PSU | raspberrypi.com / Amazon | $12 | Purchased |
| Shelly 1PM Plus | shelly.com / Amazon | $20 | Purchased |
| IP68 M20 cable gland | Amazon | $2 | Purchased |
| 0.45µm PTFE membrane (hydrophobic) | Amazon | $8–12 | Pending |
| BSS138 logic level shifter module | Amazon | $2 | Pending |
| Stainless M3/M4 hardware | Amazon / hardware store | $5 | Pending |
| PETG filament (enclosure body) | Amazon / Prusament | $20–25 | Pending |
| TPU filament Shore 95A (gasket) | Amazon | $20–25 | Pending |
