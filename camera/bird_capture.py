"""
bird_capture.py
---------------
Monitors the birdfeeder perch for motion and captures a still image
when a bird is detected. Images are saved locally to the Pi SD card.

Later versions will write to NAS via NFS mount instead.

Hardware: Arducam 64MP OwlSight on Raspberry Pi 5 (Bookworm)
Author:   Smart Birdfeeder Project
"""

import os
import time
import logging
import numpy as np
from datetime import datetime
from picamera2 import Picamera2, Preview
from libcamera import controls

# ─── SUPPRESS LIBCAMERA NOISE ────────────────────────────────────────────────
os.environ["LIBCAMERA_LOG_LEVELS"] = "ERROR"

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
# Storage — local SD card (swap path to NAS mount later)
SAVE_DIR = "/home/steve/birdfeeder/captures"

# Camera — set LensPosition for your feeder distance
# 12.0 = sharp at ~10-13cm. Adjust based on your calibration results.
LENS_POSITION = 12.0

# Image resolution — balance between detail and file size
# Full 64MP: (9152, 6944) | High quality: (4056, 3040) | Balanced: (2028, 1520)
CAPTURE_RESOLUTION = (4056, 3040)

# Motion detection sensitivity
# Lower = more sensitive (more false triggers)
# Higher = less sensitive (may miss small birds)
MOTION_THRESHOLD = 25       # pixel difference to count as changed
MOTION_MIN_PIXELS = 500     # minimum changed pixels to trigger capture

# Cooldown between captures (seconds) — prevents burst captures of same bird
CAPTURE_COOLDOWN = 5

# Frames to average for background model
BACKGROUND_FRAMES = 10

# Logging
LOG_FILE = "/home/steve/birdfeeder/bird_capture.log"

# ─── SETUP LOGGING ────────────────────────────────────────────────────────────
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ─── CAMERA SETUP ─────────────────────────────────────────────────────────────
def init_camera():
    """Initialise Arducam 64MP with manual focus and still capture config."""
    cam = Picamera2()

    # Low-resolution stream for motion detection (fast, low CPU)
    # High-resolution stream for actual captures
    config = cam.create_video_configuration(
        main={"size": CAPTURE_RESOLUTION, "format": "RGB888"},
        lores={"size": (640, 480),        "format": "YUV420"},
        display=None
    )
    cam.configure(config)
    cam.start_preview(Preview.NULL)
    cam.start()

    # Set manual focus to calibrated feeder distance
    cam.set_controls({
        "AfMode": controls.AfModeEnum.Manual,
        "LensPosition": LENS_POSITION
    })

    time.sleep(2)  # Let camera and lens settle
    log.info(f"Camera initialised — LensPosition={LENS_POSITION}, "
             f"capture resolution={CAPTURE_RESOLUTION}")
    return cam


# ─── BACKGROUND MODEL ─────────────────────────────────────────────────────────
def build_background(cam, n_frames=BACKGROUND_FRAMES):
    """
    Capture several lores frames and average them to build
    a baseline background image for motion detection.
    """
    log.info(f"Building background model from {n_frames} frames...")
    frames = []
    for _ in range(n_frames):
        frame = cam.capture_array("lores")
        # YUV420 — take Y (luma) channel only, reshape to 2D
        y_channel = frame[:480, :640].astype(np.float32)
        frames.append(y_channel)
        time.sleep(0.1)

    background = np.mean(frames, axis=0)
    log.info("Background model ready.")
    return background


# ─── MOTION DETECTION ─────────────────────────────────────────────────────────
def detect_motion(cam, background):
    """
    Compare current lores frame against background model.
    Returns True if significant motion is detected.
    """
    frame = cam.capture_array("lores")
    y_channel = frame[:480, :640].astype(np.float32)

    # Absolute difference from background
    diff = np.abs(y_channel - background)

    # Count pixels that changed more than the threshold
    changed_pixels = np.sum(diff > MOTION_THRESHOLD)

    return changed_pixels > MOTION_MIN_PIXELS, changed_pixels


# ─── CAPTURE ──────────────────────────────────────────────────────────────────
def capture_bird(cam):
    """Capture a full-resolution still and save to SAVE_DIR."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"bird_{timestamp}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)

    metadata = cam.capture_file(filepath)

    log.info(f"Captured: {filename} | "
             f"Exposure={metadata.get('ExposureTime','?')}µs | "
             f"Gain={metadata.get('AnalogueGain','?'):.2f} | "
             f"LensPos={metadata.get('LensPosition','?')}")
    return filepath


# ─── MAIN LOOP ────────────────────────────────────────────────────────────────
def main():
    log.info("=== Smart Birdfeeder Capture Starting ===")
    log.info(f"Saving images to: {SAVE_DIR}")

    cam = init_camera()
    background = build_background(cam)

    last_capture_time = 0

    log.info("Monitoring for birds... (Ctrl+C to stop)")

    try:
        while True:
            motion_detected, changed_pixels = detect_motion(cam, background)

            if motion_detected:
                now = time.time()
                if now - last_capture_time >= CAPTURE_COOLDOWN:
                    log.info(f"Motion detected — {changed_pixels} pixels changed")
                    capture_bird(cam)
                    last_capture_time = now

                    # Rebuild background after capture to account for
                    # perch state change (bird now present)
                    time.sleep(1)
                    background = build_background(cam)
                else:
                    remaining = CAPTURE_COOLDOWN - (now - last_capture_time)
                    log.debug(f"Motion detected but in cooldown "
                              f"({remaining:.1f}s remaining)")

            time.sleep(0.2)  # ~5 fps motion check rate

    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        cam.stop()
        log.info("Camera released. Exiting.")


if __name__ == "__main__":
    main()
