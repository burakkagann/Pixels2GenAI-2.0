"""
music_viz.py — synthesize a fake audio spectrum (no audio file required)
and render two classic music visualizations driven by it: a radial
spectrum (circular bars) and a horizontal spectrum (vertical bars).

The "audio" is a 64-bin spectrum that pulses on three frequency bands
(bass, mid, treble) at different rates. With no audio dependencies, the
script demonstrates the *rendering* layer of a music visualizer;
plugging in a real FFT from a real WAV is a one-function swap.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = 480
N_FRAMES = 90
FPS = 30
N_BINS = 64


def fake_spectrum(frame, n_bins=N_BINS, n_frames=N_FRAMES):
    """Three-band synthetic spectrum: bass, mid, treble with different rhythms."""
    t = frame / n_frames
    bins = np.zeros(n_bins, dtype=np.float32)

    # Bass: pulses on a 4-step rhythm
    bass = 0.6 + 0.4 * np.sin(2 * np.pi * t * 4)
    bins[:8] = bass * np.linspace(1, 0.5, 8)

    # Mid: pulses on an 8-step rhythm (faster)
    mid = 0.5 + 0.4 * np.sin(2 * np.pi * t * 8 + 0.6)
    bins[8:32] = mid * (0.7 + 0.3 * np.sin(np.arange(24) * 0.4))

    # Treble: pulses on a 16-step rhythm + small high-freq noise
    treble = 0.4 + 0.3 * np.sin(2 * np.pi * t * 16 + 1.2)
    rng = np.random.default_rng(frame * 13)
    bins[32:] = treble * (0.6 + 0.4 * rng.random(32))

    return bins.clip(0, 1)


def radial_spectrum(spectrum, size=SIZE):
    img = Image.new('RGB', (size, size), (12, 14, 22))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    inner_r = size // 6
    max_outer_r = size // 2 - 20
    n_bins = len(spectrum)

    for i, amp in enumerate(spectrum):
        angle = 2 * math.pi * i / n_bins - math.pi / 2
        # Inner ring
        x1 = cx + inner_r * math.cos(angle)
        y1 = cy + inner_r * math.sin(angle)
        # Outer ring (varies with amplitude)
        outer = inner_r + (max_outer_r - inner_r) * amp
        x2 = cx + outer * math.cos(angle)
        y2 = cy + outer * math.sin(angle)
        # Colour by band: low = warm, mid = neutral, high = cool
        if i < 8:
            color = (int(255), int(60 + amp * 100), int(80))
        elif i < 32:
            color = (int(120 + amp * 100), int(220), int(120))
        else:
            color = (int(80), int(180), int(255))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=4)

    # Centre disc
    draw.ellipse([cx - inner_r // 2, cy - inner_r // 2,
                  cx + inner_r // 2, cy + inner_r // 2],
                 fill=(50, 50, 70), outline=(120, 130, 160), width=2)
    return img


def horizontal_spectrum(spectrum, size=SIZE):
    img = Image.new('RGB', (size, size), (12, 14, 22))
    draw = ImageDraw.Draw(img)
    n_bins = len(spectrum)
    bar_w = size // n_bins
    max_h = size - 60

    for i, amp in enumerate(spectrum):
        h = int(amp * max_h)
        x0 = i * bar_w + 1
        y0 = size - 20 - h
        # Gradient by amplitude — green at low, yellow at mid, red at high
        if amp < 0.5:
            color = (int(60 + amp * 200), int(220), int(80))
        elif amp < 0.8:
            color = (int(255), int(220 - (amp - 0.5) * 300), int(60))
        else:
            color = (int(255), int(100), int(60))
        draw.rectangle([x0, y0, x0 + bar_w - 2, size - 20], fill=color)

    return img


frames = []
for f in range(N_FRAMES):
    spec = fake_spectrum(f)
    radial = radial_spectrum(spec)
    horiz = horizontal_spectrum(spec)
    # Composite side by side
    GAP = 8
    combined = Image.new('RGB', (SIZE * 2 + GAP, SIZE), (12, 14, 22))
    combined.paste(radial, (0, 0))
    combined.paste(horiz, (SIZE + GAP, 0))
    frames.append(combined)

frames[0].save(
    'music_viz.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('music_viz.png')
print(f"Saved music_viz.gif — {N_FRAMES} frames at {FPS} fps")
