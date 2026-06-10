"""
dmx_rig.py — emulate a DMX-512 lighting rig with 8 RGBW fixtures across
a stage and a programmable cue stack. Renders a top-down "stage plot"
visualisation of the cues over time.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 360)
N_FRAMES = 90
FPS = 24


# 8 RGBW fixtures spaced across the stage
N_FIX = 8


def cue_at_frame(idx, n=N_FRAMES):
    """Return the DMX channel state (one (r, g, b, intensity) per fixture)."""
    t = idx / n

    if t < 0.25:
        # Cue 1: blue wash across all
        return [(80, 110, 255, int(180)) for _ in range(N_FIX)]
    elif t < 0.5:
        # Cue 2: warm wash with subtle alternation
        return [
            (255, 180 + i * 5, 80, 230 if i % 2 == 0 else 180)
            for i in range(N_FIX)
        ]
    elif t < 0.75:
        # Cue 3: chase — one fixture bright at a time, others dim
        beat = int((t - 0.5) * 4 * N_FIX) % N_FIX
        out = []
        for i in range(N_FIX):
            if i == beat:
                out.append((255, 60, 255, 255))
            else:
                out.append((100, 60, 200, 50))
        return out
    else:
        # Cue 4: strobe — full white, intensity pulsing
        flash = 255 if (idx % 4) < 2 else 30
        return [(255, 255, 255, flash) for _ in range(N_FIX)]


def render(state, idx, size=SIZE):
    img = Image.new('RGB', size, (8, 10, 18))
    draw = ImageDraw.Draw(img)
    w, h = size

    # Stage outline
    stage_top, stage_bot = 60, h - 80
    draw.rectangle([40, stage_top, w - 40, stage_bot],
                   outline=(60, 70, 90), width=2)
    draw.text((40, 14), 'DMX-512 stage plot (8 RGBW fixtures)',
              fill=(220, 220, 240))

    # Place fixtures along the top of the stage
    fix_y = stage_top + 30
    spacing = (w - 120) / (N_FIX - 1)
    for i, (r, g, b, inten) in enumerate(state):
        fx = 60 + int(i * spacing)
        # Fixture body
        draw.rectangle([fx - 14, fix_y - 14, fx + 14, fix_y + 14],
                       fill=(40, 45, 60), outline=(120, 130, 160))
        draw.text((fx - 5, fix_y + 18), f'F{i+1}', fill=(180, 190, 210))
        # Light cone projecting down
        cone_color = (
            int(r * inten / 255), int(g * inten / 255), int(b * inten / 255)
        )
        # Render the cone as a polygon
        cone_pts = [
            (fx, fix_y + 12),
            (fx - 40, stage_bot - 8),
            (fx + 40, stage_bot - 8),
        ]
        cone_layer = Image.new('RGBA', size, (0, 0, 0, 0))
        cone_draw = ImageDraw.Draw(cone_layer)
        cone_draw.polygon(cone_pts, fill=cone_color + (160,))
        img = Image.alpha_composite(img.convert('RGBA'), cone_layer).convert('RGB')
        draw = ImageDraw.Draw(img)

    # Cue label
    t = idx / N_FRAMES
    if t < 0.25:    cue = 'Cue 1 — Blue wash'
    elif t < 0.5:   cue = 'Cue 2 — Warm alternation'
    elif t < 0.75:  cue = 'Cue 3 — Chase'
    else:           cue = 'Cue 4 — Strobe'
    draw.text((40, h - 60), cue, fill=(240, 220, 110))

    # Channel readout
    state_text = ' | '.join(
        f'F{i+1}({r:3d},{g:3d},{b:3d},{i_val:3d})'
        for i, (r, g, b, i_val) in enumerate(state[:4])
    )
    draw.text((40, h - 38), state_text + ' …',
              fill=(160, 170, 200))

    return img


frames = []
for f in range(N_FRAMES):
    state = cue_at_frame(f)
    img = render(state, f)
    frames.append(img)

frames[0].save(
    'dmx_rig.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES * 2 // 3].save('dmx_rig.png')
print(f"Saved dmx_rig.gif and dmx_rig.png — {N_FRAMES} frames")
