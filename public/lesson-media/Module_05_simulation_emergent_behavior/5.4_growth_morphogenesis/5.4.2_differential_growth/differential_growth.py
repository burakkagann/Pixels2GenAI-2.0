"""
differential_growth.py - A closed polyline grows by inserting new vertices
along edges that exceed a target spacing, while existing vertices repel
each other (short range) and are attracted to their immediate neighbours
along the curve (long range). The result is the classic crinkled,
brain-coral-like curve.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 540, 540
NUM_FRAMES = 200
FPS = 30

TARGET_SPACING = 6.5
MAX_EDGE = 1.2 * TARGET_SPACING       # split when an edge exceeds this
REPEL_RADIUS = 18.0
REPEL_STRENGTH = 0.75
NEIGHBOUR_STRENGTH = 0.10
STEPS_PER_FRAME = 2
GROWTH_INSERTIONS = 6                 # forced insertions per frame

BG = (8, 10, 18)
CURVE_COLOUR = (240, 200, 120)
SEED_RADIUS = 40
SEED_VERTICES = 42
# ----------------------------


def initial_curve():
    angles = np.linspace(0, 2 * np.pi, SEED_VERTICES, endpoint=False)
    cx, cy = WIDTH / 2, HEIGHT / 2
    xs = cx + SEED_RADIUS * np.cos(angles)
    ys = cy + SEED_RADIUS * np.sin(angles)
    return np.column_stack([xs, ys])


def relax(points):
    deltas = points[:, None, :] - points[None, :, :]
    dist = np.linalg.norm(deltas, axis=-1) + 1e-6
    np.fill_diagonal(dist, 1e6)         # large finite so 1/dist is ~0 there

    in_range = dist < REPEL_RADIUS
    falloff = np.clip((REPEL_RADIUS - dist) / REPEL_RADIUS, 0, 1)
    weight = falloff * in_range
    unit = deltas / dist[..., None]
    repel = (unit * weight[..., None]).sum(axis=1)
    points = points + REPEL_STRENGTH * repel

    prev = np.roll(points, +1, axis=0)
    nextp = np.roll(points, -1, axis=0)
    midpoint = (prev + nextp) / 2
    points = points + NEIGHBOUR_STRENGTH * (midpoint - points)
    return points


def split_long_edges(points):
    n = len(points)
    out = []
    for i in range(n):
        a = points[i]
        b = points[(i + 1) % n]
        out.append(a)
        if np.linalg.norm(b - a) > MAX_EDGE:
            out.append(0.5 * (a + b))
    return np.array(out)


def force_growth(points, rng):
    """Force the curve to grow by inserting vertices into random edges."""
    for _ in range(GROWTH_INSERTIONS):
        n = len(points)
        idx = rng.integers(0, n)
        a = points[idx]
        b = points[(idx + 1) % n]
        new_pt = 0.5 * (a + b)
        # tiny perpendicular kick so the curve actually deforms
        edge = b - a
        normal = np.array([-edge[1], edge[0]])
        normal_unit = normal / (np.linalg.norm(normal) + 1e-6)
        new_pt += normal_unit * rng.uniform(-0.4, 0.4)
        points = np.insert(points, (idx + 1) % n, new_pt, axis=0)
    return points


def render(points):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    pts = [tuple(p) for p in points] + [tuple(points[0])]
    draw.line(pts, fill=CURVE_COLOUR, width=2)
    return np.array(img)


def main():
    rng = np.random.default_rng(0)
    points = initial_curve()
    frames = []
    for frame in range(NUM_FRAMES):
        for _ in range(STEPS_PER_FRAME):
            points = relax(points)
            points = split_long_edges(points)
        points = force_growth(points, rng)
        frames.append(render(points))
        if frame == NUM_FRAMES // 2:
            Image.fromarray(frames[-1]).save('differential_frame.png')

    imageio.mimsave('differential_growth.gif', frames, fps=FPS)
    Image.fromarray(frames[-1]).save('differential_final.png')
    print(f'Wrote differential_growth.gif (final {len(points)} vertices)')


if __name__ == '__main__':
    main()
