"""
bar_chart_race.py — render an animated bar-chart race driven by a small
synthetic dataset. Five categories compete over 12 time steps; bars
interpolate smoothly between data points and resort themselves as
ranks change.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


CANVAS_W, CANVAS_H = 720, 480
N_STEPS = 12
FRAMES_PER_STEP = 12
N_FRAMES = N_STEPS * FRAMES_PER_STEP
MARGIN = 60

CATEGORIES = ['Python', 'JavaScript', 'Rust', 'Go', 'Julia']
COLORS = [
    (61, 119, 180),    # Python blue
    (240, 200, 60),    # JS yellow
    (220, 90, 60),     # Rust orange
    (90, 200, 220),    # Go cyan
    (155, 110, 200),   # Julia purple
]

# Synthetic time series: each row is a time step, each column a category
rng = np.random.default_rng(7)
trajectories = []
state = np.array([50, 45, 5, 20, 8], dtype=np.float64)
trajectories.append(state.copy())
for _ in range(N_STEPS - 1):
    state = state + rng.normal([2.5, -1, 8, 4, 6], 2.0, size=5)
    state = np.clip(state, 0, 200)
    trajectories.append(state.copy())
DATA = np.array(trajectories)  # shape (N_STEPS, 5)


def ease_in_out(t):
    return np.where(t < 0.5, 2 * t * t, 1 - (-2 * t + 2) ** 2 / 2)


def render_frame(frame):
    # Determine the source and target step + fractional progress within step
    step = frame // FRAMES_PER_STEP
    frac = (frame % FRAMES_PER_STEP) / FRAMES_PER_STEP
    progress = ease_in_out(np.array([frac]))[0]

    if step >= N_STEPS - 1:
        values = DATA[N_STEPS - 1].copy()
    else:
        values = DATA[step] * (1 - progress) + DATA[step + 1] * progress

    # Sort by value descending
    order = np.argsort(-values)

    img = Image.new('RGB', (CANVAS_W, CANVAS_H), (20, 22, 32))
    draw = ImageDraw.Draw(img)

    # Title
    try:
        font = ImageFont.truetype('arial.ttf', 18)
        title_font = ImageFont.truetype('arial.ttf', 28)
    except Exception:
        font = title_font = ImageFont.load_default()

    draw.text((MARGIN, 18), 'Language Popularity (synthetic data)',
              fill=(220, 220, 230), font=title_font)
    year_display = 2014 + step + progress
    draw.text((CANVAS_W - 100, 22),
              f'Year {year_display:.1f}', fill=(200, 200, 220), font=font)

    # Bars
    bar_h = (CANVAS_H - 110) // len(CATEGORIES)
    label_x = MARGIN
    bar_x = MARGIN + 100
    max_bar = CANVAS_W - bar_x - MARGIN
    max_val = max(values) * 1.05

    # Animate the y-position of each category based on rank.
    # ranks[i] = current rank of category i (0 = top)
    ranks = np.argsort(np.argsort(-values))
    for i, cat in enumerate(CATEGORIES):
        y = 80 + ranks[i] * bar_h + bar_h // 4
        w = int((values[i] / max_val) * max_bar)
        # Bar
        draw.rectangle([bar_x, y, bar_x + w, y + bar_h - 16], fill=COLORS[i])
        # Category label
        draw.text((label_x, y - 2), cat, fill=COLORS[i], font=font)
        # Value
        draw.text((bar_x + w + 8, y - 2),
                  f'{values[i]:.0f}', fill=(220, 220, 230), font=font)

    return img


frames = [render_frame(f) for f in range(N_FRAMES)]
# Hold the end
for _ in range(20):
    frames.append(frames[-1].copy())

frames[0].save(
    'bar_chart_race.gif',
    save_all=True,
    append_images=frames[1:],
    duration=50,
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('bar_chart_midpoint.png')
print(f"Saved bar_chart_race.gif — {len(frames)} frames, {N_STEPS} time steps")
