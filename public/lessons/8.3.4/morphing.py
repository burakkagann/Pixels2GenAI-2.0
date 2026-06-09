"""
morphing.py — render three classical scene-to-scene transitions on a
pair of images: crossfade, wipe, and a kaleidoscopic mosaic dissolve.
Each transition is a per-pixel blend driven by an alpha map that
varies in time, space, or both.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = 360
N_FRAMES = 60
FPS = 30


def synth_image(seed, size=SIZE, kind='warm'):
    rng = np.random.default_rng(seed)
    img = np.zeros((size, size, 3), dtype=np.uint8)
    yy, xx = np.mgrid[:size, :size]
    cx, cy = rng.integers(size // 3, 2 * size // 3, 2)
    if kind == 'warm':
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        img[..., 0] = (255 - (r * 0.3).clip(0, 200)).astype(np.uint8)
        img[..., 1] = (200 - (r * 0.4).clip(0, 180)).astype(np.uint8)
        img[..., 2] = (100 - (r * 0.2).clip(0, 80)).astype(np.uint8)
        # Add a few accent dots
        for _ in range(20):
            ax = int(rng.integers(0, size))
            ay = int(rng.integers(0, size))
            img[max(0, ay - 6):ay + 6, max(0, ax - 6):ax + 6] = (255, 220, 90)
    else:
        # cool palette
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        img[..., 0] = (40 + (r * 0.2).clip(0, 80)).astype(np.uint8)
        img[..., 1] = (150 - (r * 0.3).clip(0, 100)).astype(np.uint8)
        img[..., 2] = (255 - (r * 0.4).clip(0, 200)).astype(np.uint8)
        # White stars
        for _ in range(40):
            ax = int(rng.integers(0, size))
            ay = int(rng.integers(0, size))
            img[ay, ax] = (240, 240, 250)
    return img


def crossfade(a, b, t):
    return (a * (1 - t) + b * t).astype(np.uint8)


def wipe(a, b, t):
    """Horizontal wipe — a soft transition band sweeps left to right."""
    h, w, _ = a.shape
    band_w = 80
    centre = int((w + band_w) * t - band_w / 2)
    xs = np.arange(w)
    # Per-column alpha: 0 left of band, 1 right of band, smooth ramp in band
    alpha = np.clip((xs - (centre - band_w / 2)) / band_w, 0, 1)
    alpha2 = alpha[None, :, None]
    return (a * (1 - alpha2) + b * alpha2).astype(np.uint8)


def mosaic(a, b, t, tile=20):
    """Mosaic dissolve — each tile flips from a to b at a per-tile threshold."""
    h, w, _ = a.shape
    n_y, n_x = h // tile, w // tile
    # Per-tile threshold drawn from a hash of (y, x) — stable across frames
    rng = np.random.default_rng(42)
    thresholds = rng.uniform(0, 1, (n_y, n_x))
    out = a.copy()
    for ty in range(n_y):
        for tx in range(n_x):
            if thresholds[ty, tx] < t:
                y0, x0 = ty * tile, tx * tile
                out[y0:y0 + tile, x0:x0 + tile] = b[y0:y0 + tile, x0:x0 + tile]
    return out


img_a = synth_image(11, kind='warm')
img_b = synth_image(7, kind='cool')

Image.fromarray(img_a).save('scene_a.png')
Image.fromarray(img_b).save('scene_b.png')

# Build three side-by-side comparison animations
def transition_strip(t_value):
    """Return a horizontal strip showing crossfade, wipe, mosaic at given t."""
    cf = crossfade(img_a, img_b, t_value)
    wp = wipe(img_a, img_b, t_value)
    mo = mosaic(img_a, img_b, t_value)
    GAP = 6
    h, w, _ = img_a.shape
    strip = np.full((h, w * 3 + GAP * 2, 3), 18, dtype=np.uint8)
    strip[:, :w] = cf
    strip[:, w + GAP:2 * w + GAP] = wp
    strip[:, 2 * w + 2 * GAP:] = mo
    return Image.fromarray(strip)


frames = []
for f in range(N_FRAMES):
    t = f / (N_FRAMES - 1)
    frames.append(transition_strip(t))

# Hold the final state
for _ in range(10):
    frames.append(frames[-1].copy())

frames[0].save(
    'morphing_strip.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('morphing_midpoint.png')
print(f"Saved morphing_strip.gif and morphing_midpoint.png")
