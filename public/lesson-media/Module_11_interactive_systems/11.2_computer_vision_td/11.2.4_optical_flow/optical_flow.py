"""
optical_flow.py — compute Lucas-Kanade-style dense optical flow on a
synthetic moving scene (sliding texture + spinning disc) and render it
as an arrow field overlaid on the source. Pure NumPy implementation of
the gradient-based flow estimator.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (400, 300)
N_FRAMES = 36
WINDOW = 8  # half-window for the Lucas-Kanade least-squares


def synth_pair(idx, n=N_FRAMES, size=SIZE):
    """Generate a frame pair (t, t+1) with known motion."""
    w, h = size

    # Background: textured wall sliding right
    rng = np.random.default_rng(0)
    wall = rng.integers(0, 255, (h + 20, w + 60), dtype=np.uint8)
    wall = (wall.astype(np.float32) * 0.4 + 80).astype(np.uint8)

    shift = (idx * 2) % 40    # keep within the padded wall
    A_bg = wall[10:10 + h, shift:shift + w].copy()
    B_bg = wall[10:10 + h, shift + 2:shift + 2 + w].copy()

    # Defensive crop to (h, w) in case of off-by-one
    A_bg = A_bg[:h, :w]
    B_bg = B_bg[:h, :w]
    if A_bg.shape != (h, w):
        A_bg = np.pad(A_bg, ((0, h - A_bg.shape[0]), (0, w - A_bg.shape[1])), mode='edge')
    if B_bg.shape != (h, w):
        B_bg = np.pad(B_bg, ((0, h - B_bg.shape[0]), (0, w - B_bg.shape[1])), mode='edge')

    # Foreground: a darker spinning disc
    yy, xx = np.mgrid[:h, :w]
    cx, cy = w // 2, h // 2
    disc = (xx - cx) ** 2 + (yy - cy) ** 2 < 50 ** 2

    angle1 = idx * 0.15
    angle2 = (idx + 1) * 0.15
    spokes_a = np.cos(np.arctan2(yy - cy, xx - cx) * 6 - angle1) > 0
    spokes_b = np.cos(np.arctan2(yy - cy, xx - cx) * 6 - angle2) > 0

    A = A_bg.copy()
    B = B_bg.copy()
    A[disc & spokes_a] = 60
    A[disc & ~spokes_a] = 220
    B[disc & spokes_b] = 60
    B[disc & ~spokes_b] = 220
    return A, B


def lucas_kanade_flow(prev, nxt, window=WINDOW, step=16):
    """Sparse Lucas-Kanade flow at a grid of points (step pixels apart).

    Returns lists of (x, y, dx, dy)."""
    prev_f = prev.astype(np.float32)
    nxt_f = nxt.astype(np.float32)
    h, w = prev.shape

    # Image gradients
    Ix = np.gradient(prev_f, axis=1)
    Iy = np.gradient(prev_f, axis=0)
    It = nxt_f - prev_f

    flow_points = []
    for y in range(window, h - window, step):
        for x in range(window, w - window, step):
            Ix_win = Ix[y - window:y + window + 1, x - window:x + window + 1].ravel()
            Iy_win = Iy[y - window:y + window + 1, x - window:x + window + 1].ravel()
            It_win = It[y - window:y + window + 1, x - window:x + window + 1].ravel()

            # Solve [Ix Iy] [u v]^T = -It in least squares
            A_mat = np.stack([Ix_win, Iy_win], axis=1)
            b = -It_win
            try:
                uv, *_ = np.linalg.lstsq(A_mat, b, rcond=None)
            except np.linalg.LinAlgError:
                continue
            u, v = uv
            if not np.isfinite(u) or not np.isfinite(v):
                continue
            # Reject very small or huge motions (noise / divergent solves)
            mag = math.hypot(u, v)
            if mag < 0.3 or mag > 12:
                continue
            flow_points.append((x, y, float(u), float(v)))

    return flow_points


def render_flow(arr_color, flow_points):
    img = Image.fromarray(arr_color).convert('RGB')
    draw = ImageDraw.Draw(img)
    for x, y, u, v in flow_points:
        end_x = x + u * 3      # exaggerate for visibility
        end_y = y + v * 3
        # Colour by direction (hue) and magnitude (brightness)
        mag = math.hypot(u, v)
        b = int(min(255, 80 + mag * 20))
        col = (int(220 - mag * 8), b, int(120 + mag * 10))
        draw.line([(x, y), (end_x, end_y)], fill=col, width=2)
        draw.ellipse([end_x - 2, end_y - 2, end_x + 2, end_y + 2], fill=col)
    return img


frames = []
for f in range(N_FRAMES):
    A, B = synth_pair(f)
    flow = lucas_kanade_flow(A, B)
    color_A = np.stack([A] * 3, axis=-1)
    img = render_flow(color_A, flow)
    frames.append(img)

frames[0].save(
    'optical_flow.gif',
    save_all=True,
    append_images=frames[1:],
    duration=100,
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('optical_flow.png')
print(f"Saved optical_flow.gif and optical_flow.png — {N_FRAMES} frames")
