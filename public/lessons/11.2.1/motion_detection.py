"""
motion_detection.py — extend frame differencing into a proper background
subtraction pipeline. Uses a running-average background model so it
tolerates slow lighting changes and small camera shake, while still
firing on people walking through the frame.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (480, 360)
N_FRAMES = 80


def synth_scene(idx, n=N_FRAMES, size=SIZE):
    """Generate a frame: a static room + a walking figure."""
    w, h = size
    arr = np.full((h, w, 3), [54, 60, 78], dtype=np.uint8)

    rng = np.random.default_rng(0)
    arr = np.clip(arr.astype(np.int32) + rng.integers(-10, 10, (h, w, 3),
                                                       dtype=np.int32),
                  0, 255).astype(np.uint8)

    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 200, 220, 320], fill=(100, 80, 60))   # table
    draw.rectangle([320, 60, 460, 300], fill=(70, 90, 130))   # cabinet
    draw.line([(0, 320), (w, 320)], fill=(80, 60, 40), width=3)  # floor line

    # Walking figure: appears at frame 10, walks across, disappears
    if 10 <= idx < n - 10:
        t = (idx - 10) / (n - 20)
        px = int(20 + t * (w - 70))
        py = h - 110 + int(4 * math.sin(idx * 0.7))   # subtle bob
        # Torso
        draw.ellipse([px, py, px + 40, py + 70], fill=(220, 110, 90))
        # Head
        draw.ellipse([px + 8, py - 32, px + 32, py - 4], fill=(240, 200, 170))

    return np.array(img)


def to_gray(arr):
    return (arr[..., 0] * 0.114 + arr[..., 1] * 0.587 + arr[..., 2] * 0.299).astype(np.uint8)


def render_motion(curr, mask):
    """Overlay green where motion was detected."""
    out = curr.copy()
    out[mask > 0] = [40, 240, 90]
    blend = (0.6 * curr + 0.4 * out).astype(np.uint8)
    return blend


# Build background model: running average of first 10 background frames
bg = None
alpha = 0.05  # background-update rate; smaller = slower
frames = []

for f in range(N_FRAMES):
    cur = synth_scene(f)
    gray = to_gray(cur).astype(np.float32)

    if bg is None:
        bg = gray.copy()
    else:
        # Only update the background where motion is NOT detected
        diff = np.abs(gray - bg)
        motion_mask = (diff > 22).astype(np.uint8) * 255

        # Update background on still pixels
        still = motion_mask == 0
        bg[still] = (1 - alpha) * bg[still] + alpha * gray[still]

        rendered = render_motion(cur, motion_mask)
    if f == 0:
        rendered = cur
    frames.append(Image.fromarray(rendered))

frames[0].save(
    'motion_detection.gif',
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('motion_detection.png')
print(f"Saved motion_detection.gif and motion_detection.png — {N_FRAMES} frames")
