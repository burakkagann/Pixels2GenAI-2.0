"""
sprite_sheet.py — build a sprite sheet (8 frames of a bouncing ball)
and play it back as an animated GIF. Demonstrates the canonical 2D-game
animation pattern: render a fixed-size grid of poses once, then animate
by indexing into the grid with a frame counter.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


CELL = 96
COLS, ROWS = 8, 1
SHEET_W, SHEET_H = CELL * COLS, CELL * ROWS


def render_pose(frame_idx, n_frames=8):
    """Render one pose of a bouncing ball into a CELL-sized RGBA tile."""
    img = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Vertical position: parabola peaking mid-loop
    t = frame_idx / (n_frames - 1)
    # arch shape — ball lifts off ground, peaks at t=0.5, lands
    height = -4 * (t - 0.5) ** 2 + 1     # peak = 1, edges = 0
    height = max(0, height)

    # Squash + stretch
    on_ground = height < 0.05
    rx = 22 if not on_ground else 28
    ry = 22 if not on_ground else 16

    cx = CELL // 2
    cy = int(CELL - 18 - height * 50)    # 50 px peak displacement

    # Shadow on the floor
    shadow_alpha = int(120 - height * 100)
    draw.ellipse(
        [cx - 24, CELL - 10, cx + 24, CELL - 4],
        fill=(0, 0, 0, max(20, shadow_alpha)),
    )

    # Ball
    draw.ellipse(
        [cx - rx, cy - ry, cx + rx, cy + ry],
        fill=(255, 110, 90, 255), outline=(60, 25, 25, 255), width=2,
    )

    # Highlight
    draw.ellipse(
        [cx - rx + 4, cy - ry + 4, cx - rx + 14, cy - ry + 14],
        fill=(255, 220, 200, 240),
    )
    return img


# Build the sprite sheet
sheet = Image.new('RGBA', (SHEET_W, SHEET_H), (24, 28, 38, 255))
for i in range(COLS):
    sheet.paste(render_pose(i), (i * CELL, 0), render_pose(i))

# Draw cell separators on the sheet for clarity
draw = ImageDraw.Draw(sheet)
for i in range(1, COLS):
    draw.line([(i * CELL, 0), (i * CELL, SHEET_H)], fill=(60, 65, 80))
sheet.save('sprite_sheet.png')

# Build the animation by indexing into the sheet
frames = []
for frame in range(COLS):
    cell = sheet.crop((frame * CELL, 0, (frame + 1) * CELL, CELL))
    bg = Image.new('RGB', (CELL, CELL), (24, 28, 38))
    bg.paste(cell, (0, 0), cell.convert('RGBA'))
    frames.append(bg)

frames[0].save(
    'bounce_animation.gif',
    save_all=True,
    append_images=frames[1:],
    duration=100,
    loop=0,
    optimize=True,
)

print(f"Saved sprite_sheet.png ({COLS}x{ROWS}) and bounce_animation.gif")
