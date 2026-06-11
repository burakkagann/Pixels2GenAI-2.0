"""
differential_starter.py - Exercise 3 scaffold.

The growth and rendering are wired up. You implement `relax()` - the
repulsion + smoothing pass.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 540, 540
TARGET_SPACING = 6.5
REPEL_RADIUS = 18.0
REPEL_STRENGTH = 0.75
NEIGHBOUR_STRENGTH = 0.10
NUM_FRAMES = 150
FPS = 30
GROWTH_INSERTIONS = 5


def relax(points):
    """TODO: implement two forces.

    1. Repulsion: for each point, sum unit vectors from every neighbour
       within REPEL_RADIUS, weighted by ((REPEL_RADIUS - dist) / REPEL_RADIUS).
       Add REPEL_STRENGTH * sum to position.

    2. Smoothing: each point is pulled NEIGHBOUR_STRENGTH of the way toward
       the midpoint of its two curve-neighbours (use np.roll +/-1).
    """
    return points


def force_growth(points, rng):
    for _ in range(GROWTH_INSERTIONS):
        n = len(points)
        idx = rng.integers(0, n)
        a = points[idx]
        b = points[(idx + 1) % n]
        new_pt = 0.5 * (a + b)
        edge = b - a
        normal = np.array([-edge[1], edge[0]])
        new_pt += normal / (np.linalg.norm(normal) + 1e-6) * rng.uniform(-0.4, 0.4)
        points = np.insert(points, (idx + 1) % n, new_pt, axis=0)
    return points


def render(points):
    img = Image.new('RGB', (WIDTH, HEIGHT), (8, 10, 18))
    draw = ImageDraw.Draw(img)
    pts = [tuple(p) for p in points] + [tuple(points[0])]
    draw.line(pts, fill=(240, 200, 120), width=2)
    return np.array(img)


def main():
    rng = np.random.default_rng(0)
    angles = np.linspace(0, 2 * np.pi, 36, endpoint=False)
    cx, cy = WIDTH / 2, HEIGHT / 2
    points = np.column_stack([cx + 40 * np.cos(angles), cy + 40 * np.sin(angles)])
    frames = []
    for _ in range(NUM_FRAMES):
        points = relax(points)
        points = relax(points)
        points = force_growth(points, rng)
        frames.append(render(points))
    imageio.mimsave('differential_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
