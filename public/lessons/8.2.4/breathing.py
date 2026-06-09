"""
breathing.py — three subtle ambient-life animations on a still image:
breathing (vertical scale), pulsing (uniform scale), and channel-roll glitch.
Each one is a tiny modulation that turns a static image into a living one.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = 320
N_FRAMES = 90
FPS = 30


def synth_face(size=SIZE):
    """Procedurally render a friendly head-and-shoulders silhouette."""
    img = Image.new('RGB', (size, size), (24, 28, 38))
    draw = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    # Shoulders
    draw.ellipse([cx - 110, cy + 30, cx + 110, cy + 200],
                 fill=(220, 200, 170))
    # Neck
    draw.rectangle([cx - 22, cy + 5, cx + 22, cy + 55],
                   fill=(220, 200, 170))
    # Head
    draw.ellipse([cx - 60, cy - 90, cx + 60, cy + 30],
                 fill=(240, 220, 195))
    # Hair
    draw.chord([cx - 60, cy - 100, cx + 60, cy + 20], 200, 340,
               fill=(70, 50, 40))
    # Eyes
    for sign in (-1, 1):
        ex = cx + sign * 18
        ey = cy - 32
        draw.ellipse([ex - 4, ey - 3, ex + 4, ey + 3], fill=(40, 40, 60))
    # Mouth
    draw.arc([cx - 12, cy - 20, cx + 12, cy + 0], 0, 180,
             fill=(120, 60, 60), width=2)
    return img


def breathing_frame(base, t):
    """Scale vertically by 1 + 0.025 * sin(2*pi*t)."""
    scale_y = 1.0 + 0.025 * math.sin(2 * math.pi * t)
    H, W = base.size[1], base.size[0]
    new_h = int(H * scale_y)
    scaled = base.resize((W, new_h), resample=Image.BILINEAR)
    out = Image.new('RGB', (W, H), (24, 28, 38))
    # Anchor at the bottom — chest expands upward
    out.paste(scaled, (0, H - new_h))
    return out


def pulsing_frame(base, t):
    """Uniform scale 1 + 0.04 * sin(2*pi*t)."""
    scale = 1.0 + 0.04 * math.sin(2 * math.pi * t)
    H, W = base.size[1], base.size[0]
    new_h = int(H * scale)
    new_w = int(W * scale)
    scaled = base.resize((new_w, new_h), resample=Image.BILINEAR)
    out = Image.new('RGB', (W, H), (24, 28, 38))
    out.paste(scaled, ((W - new_w) // 2, (H - new_h) // 2))
    return out


def glitch_frame(base, t):
    """Channel-roll glitch: shift blue and green by small sinusoidal amounts."""
    arr = np.array(base)
    dx_b = int(8 * math.sin(2 * math.pi * t))
    dy_g = int(4 * math.sin(2 * math.pi * t + math.pi / 2))
    arr[:, :, 2] = np.roll(arr[:, :, 2], dx_b, axis=1)
    arr[:, :, 1] = np.roll(arr[:, :, 1], dy_g, axis=0)
    return Image.fromarray(arr)


face = synth_face()
face.save('subject.png')

frames_b, frames_p, frames_g = [], [], []
for i in range(N_FRAMES):
    t = i / N_FRAMES
    frames_b.append(breathing_frame(face, t))
    frames_p.append(pulsing_frame(face, t))
    frames_g.append(glitch_frame(face, t))


def save_gif(name, frames, fps=FPS):
    frames[0].save(
        name,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True,
    )


save_gif('breathing.gif', frames_b)
save_gif('pulsing.gif', frames_p)
save_gif('glitch.gif', frames_g)

# Composite still: three frames side by side
mid = N_FRAMES // 2
composite = Image.new('RGB', (SIZE * 3, SIZE), (24, 28, 38))
composite.paste(frames_b[mid], (0, 0))
composite.paste(frames_p[mid], (SIZE, 0))
composite.paste(frames_g[mid], (SIZE * 2, 0))
composite.save('three_pulses.png')

print(f"Saved breathing.gif, pulsing.gif, glitch.gif — {N_FRAMES} frames each at {FPS} fps")
