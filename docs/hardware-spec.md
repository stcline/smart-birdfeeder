# Smart Birdfeeder — Hardware Specification

This document captures all hardware decisions made during the initial design phase. Update this file when components change; move superseded versions to `/archive`.

---

## Compute

| Component | Model | Notes |
|---|---|---|
| Single-board computer | Raspberry Pi 5 (4GB or 8GB) | Main compute for Frigate NVR, BirdWeather API poller, and Flask dashboard |

---

## Power

| Component | Model | Notes |
|---|---|---|
| AC-DC converter | Mean Well IRM-30-5 | 5V / 6A / 30W; encapsulated, screw terminals; mounted in a separate weatherproof junction box on the post near the outlet — not inside the birdfeeder enclosure; ~$14 |
| AC power source | Existing outdoor outlet at post | Standard 3-prong outlet; converter AC side wired L (black/hot), N (white/neutral); bare ground capped or tied to metal box |
| DC wiring | 18 AWG stranded, red/black, UV-rated | Runs from converter junction box to birdfeeder enclosure via coupler and IP68 cable gland |
| Inline fuse | 5A mini blade fuse, weatherproof holder | On DC positive line between converter and enclosure |
| DC coupler | User-supplied | Allows birdfeeder enclosure to be disconnected from power without cutting wires |
| Cable gland | IP68, M20 | Single DC cable penetration on bottom or side face of enclosure |
| Pi connection | GPIO header — Pin 2 (5V) + Pin 6 (GND) | Bypasses USB-C; direct regulated DC to GPIO. **Verify polarity before powering on — no reverse-polarity protection on this path** |

> **Note:** PoE was considered but not used — no Ethernet run is available at the installation location. Network connectivity is via the Pi 5's built-in Wi-Fi.

---

## Cooling

Three-layer cooling strategy for outdoor enclosure use (Cypress, CA — high ambient summer temps).

| Component | Model | Purpose | Control |
|---|---|---|---|
| SoC cooler | [Official Raspberry Pi Active Cooler](https://www.raspberrypi.com/products/active-cooler/) | Cools Pi 5 SoC directly; mounts directly on Pi 5 — no HAT in this build | Pi firmware — automatic PWM |
| Enclosure exhaust fan | [Noctua NF-A4x10 5V PWM](https://www.amazon.com/Noctua-NF-A4x10-5V-PWM-Premium/dp/B07DXS86G7/) (ASIN: B07DXS86G7) | Exhausts hot air from electronics compartment through louvered vent | GPIO PWM script — temperature-triggered (~65°C on, 100% at 75°C+) |

### Enclosure Cooling Design Notes
- Electronics compartment is physically separated from birdseed compartment by an internal partition
- Noctua fan mounts in a 40mm cutout in the electronics compartment wall (4× M3 holes on 32mm bolt circle)
- Fan exhausts outward; intake is a filtered/louvered vent on the opposite face (bottom preferred for rain protection)
- Light-colored exterior to minimize solar gain
- Shade overhang over the electronics compartment face recommended
- A BSS138 logic level shifter (3.3V → 5V) is recommended between the GPIO PWM pin and the Noctua fan's PWM wire for full speed ramping; alternatively, wire for on/off control only
- Pi SoC temperature is monitored via `vcgencmd measure_temp` and surfaced in the dashboard

### Full Stack Height
The Pi 5 + Official Active Cooler stacked height should be confirmed from the Raspberry Pi documentation before finalizing the electronics compartment height in Fusion 360.

---

## Camera

| Option | Model | Focal Length | FoV (H) | Resolution | Notes |
|---|---|---|---|---|---|
| Preferred | Pi Camera Module 3 (standard) | 4.74mm | 66° | 12MP (Sony IMX708) | Motorized autofocus, F1.8, focus 10cm–∞; good balance for feeder distance |
| Alternative | Arducam 64MP OwlSight | 6.65mm | 68° | 64MP | Tighter framing, more crop room; F1.9, focus 12cm–∞ |
| Avoid | Pi Camera Module 3 Wide | 2.75mm | 102° | 12MP | Too wide for close feeder; edge distortion |

> **Decision pending:** Camera model not yet finalized. Both connect via CSI ribbon to the Pi 5 (uses smaller CSI connector than Pi 4 — adapter cable required for standard modules).

---

## Bird Audio Detection

| Component | Model | Notes |
|---|---|---|
| Audio detector | [Haikubox](https://haikubox.com) | Existing hardware — kept in place; reports to BirdWeather platform |
| API integration | [BirdWeather API](https://app.birdweather.com/api/v1/) | Polled by Python script in `/haikubox`; detections merged into local SQLite database |

No additional audio hardware is planned for this project. The Haikubox handles all audio-based species identification.

---

## Media Storage

| Component | Notes |
|---|---|
| NAS (to be built) | Separate NAS build — see NAS project thread |
| Protocol | NFS mount from Pi to NAS |
| Mount point | Defined in `/config` and `/scripts/mount_nas.sh` |
| Frigate media dir | Points to NFS mount — clips and snapshots written directly to NAS |
| Dashboard access | Flask app reads clips from same NFS mount path |

### NAS Integration Requirements (for NAS build thread)
- Must support NFS exports (NFSv3 or NFSv4)
- Recommend minimum 2-bay with RAID 1 for redundancy
- Suggested directory structure on NAS:
  ```
  /birdfeeder/
    clips/        ← Frigate motion-triggered video clips
    snapshots/    ← Frigate species ID snapshots
  ```
- Network must be on same LAN segment as Pi (or routed with stable IP)
- Static IP or DHCP reservation recommended for NAS

---

## Optional Upgrades (Not in Initial Build)

| Component | Purpose | Notes |
|---|---|---|
| Google Coral USB Accelerator | Offloads Frigate object detection from CPU | Adds ~$60–80; plug-and-play USB 3.0; Frigate supports with one config line change; add if CPU temps or detection FPS are problematic after initial deployment |

---

## Shopping List Summary

| Item | Source | Approx. Cost |
|---|---|---|
| Raspberry Pi 5 (4GB or 8GB) | raspberrypi.com / Amazon | $60–80 |
| Official Pi 5 Active Cooler | raspberrypi.com / Amazon | $5 |
| Noctua NF-A4x10 5V PWM (ASIN: B07DXS86G7) | [Amazon](https://www.amazon.com/dp/B07DXS86G7) | $16 |
| Pi Camera Module 3 (standard) — or Arducam 64MP | raspberrypi.com / Amazon | $25–50 |
| Mean Well IRM-30-5 AC-DC converter | Amazon / Digi-Key | $14 |
| Weatherproof junction box for converter (post-mount) | Amazon | $8–12 |
| Weatherproof in-use outlet cover | Amazon | $8 |
| 18 AWG stranded DC wire, red/black, UV-rated | Amazon | $8 |
| 5A inline fuse holder, weatherproof | Amazon | $5 |
| IP68 M20 cable gland | Amazon | $2 |
| BSS138 logic level shifter module | Amazon | $2 |
| Stainless M3/M4 hardware (screws, nuts) | Amazon / hardware store | $5 |
