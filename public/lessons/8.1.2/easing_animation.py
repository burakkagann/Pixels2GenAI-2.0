"""
easing_animation.py — render four moving dots traveling left to right
across a strip, each driven by a different easing function: linear,
ease-in cubic, ease-out cubic, and ease-in-out cubic. Save the result as
an animated GIF so the perceptual difference is impossible to miss.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw


WIDTH, HEIGHT = 640, 260
FPS = 30
DURATION_S = 2.5
N_FRAMES = int(FPS * DURATION_S)

ROW_LABELS = ['linear', 'ease-in cubic', 'ease-out cubic', 'ease-in-out cubic']
ROW_COLORS = [
    (200, 200, 200),
    (255, 150, 80),
    (110, 200, 255),
    (180, 130, 255),
]

ROW_HEIGHT = HEIGHT // (len(ROW_LABELS) + 1)
MARGIN_X = 60
TRAVEL = WIDTH - 2 * MARGIN_X


def ease(name, t):
    if name == 'linear':
        return t
    if name == 'ease-in cubic':
        return t ** 3
    if name == 'ease-out cubic':
        return 1 - (1 - t) ** 3
    if name == 'ease-in-out cubic':
        return np.where(t < 0.5, 4 * t ** 3, 1 - (-2 * t + 2) ** 3 / 2)
    raise ValueError(name)


frames = []
for f in range(N_FRAMES):
    t = f / (N_FRAMES - 1)
    img = Image.new('RGB', (WIDTH, HEIGHT), (16, 18, 28))
    draw = ImageDraw.Draw(img)

    for r, (name, color) in enumerate(zip(ROW_LABELS, ROW_COLORS)):
        y = (r + 1) * ROW_HEIGHT
        # Track line
        draw.line([(MARGIN_X, y), (MARGIN_X + TRAVEL, y)], fill=(45, 50, 65), width=1)
        # End markers
        draw.line([(MARGIN_X, y - 6), (MARGIN_X, y + 6)], fill=(80, 85, 100))
        draw.line(
            [(MARGIN_X + TRAVEL, y - 6), (MARGIN_X + TRAVEL, y + 6)],
            fill=(80, 85, 100),
        )

        # Dot position from easing
        x = MARGIN_X + int(TRAVEL * ease(name, t))
        draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=color)

        # Label
        draw.text((10, y - 8), name, fill=color)

    frames.append(img)

# Append a few held end-state frames so the GIF has a clear "settled" pause.
for _ in range(int(FPS * 0.5)):
    frames.append(frames[-1].copy())

frames[0].save(
    'easing_animation.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
print(f"Saved easing_animation.gif — {len(frames)} frames at {FPS} fps")
