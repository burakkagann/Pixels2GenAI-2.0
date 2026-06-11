"""
ARCHIVED one-shot from the flat-layout era: writes into public/lessons/<id>/,
which the 2026-06 restructure replaced with public/lesson-media/<module>/<subtopic>/<leaf>/.
Outputs are already committed; rework the paths before ever running again.

Generate missing figure assets for from-scratch Module 03 lessons.

Lessons 3.2.4 (Blend Modes) and 3.3.4 (Voronoi Diagrams) were
written from scratch because v1 stubs had no figures. This script
generates the figures the MDX references.

Usage:
    python scripts/gen-module-03-figures.py
"""

from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "public" / "lessons"


def two_gradients(size):
    y, x = np.mgrid[:size, :size] / size
    A = np.stack([x, y, np.full_like(x, 0.3)], axis=-1)
    B = np.stack([np.full_like(x, 0.5), 1 - x, 1 - y], axis=-1)
    return A, B


def gen_multiply_demo():
    """3.2.4 — multiply blend of two coloured gradients."""
    SIZE = 400
    A, B = two_gradients(SIZE)
    out = (A * B * 255).astype(np.uint8)
    Image.fromarray(out).save(LESSONS_DIR / "3.2.4" / "multiply_demo.png")
    print("wrote 3.2.4/multiply_demo.png")


def gen_blend_modes_grid():
    """3.2.4 — 5-panel blend-mode grid."""
    SIZE = 200
    GUTTER = 6
    A, B = two_gradients(SIZE)

    def multiply(A, B):
        return A * B

    def screen(A, B):
        return 1 - (1 - A) * (1 - B)

    def overlay(A, B):
        return np.where(A < 0.5, 2 * A * B, 1 - 2 * (1 - A) * (1 - B))

    def difference(A, B):
        return np.abs(A - B)

    def add(A, B):
        return A + B

    panels = [
        multiply(A, B),
        screen(A, B),
        overlay(A, B),
        difference(A, B),
        add(A, B),
    ]

    gutter = np.zeros((SIZE, GUTTER, 3), dtype=np.float64)
    pieces = []
    for i, panel in enumerate(panels):
        pieces.append(panel)
        if i < len(panels) - 1:
            pieces.append(gutter)
    grid = np.hstack(pieces)

    out = (np.clip(grid, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out).save(LESSONS_DIR / "3.2.4" / "blend_modes_grid.png")
    print("wrote 3.2.4/blend_modes_grid.png")


def gen_voronoi():
    """3.3.4 — 12-seed Voronoi diagram."""
    SIZE = 400
    NUM_SEEDS = 12
    rng = np.random.default_rng(0)

    seeds = rng.integers(0, SIZE, size=(NUM_SEEDS, 2))
    y, x = np.indices((SIZE, SIZE))
    dy = y[..., None] - seeds[:, 0]
    dx = x[..., None] - seeds[:, 1]
    dist_sq = dy * dy + dx * dx
    labels = np.argmin(dist_sq, axis=-1)

    palette = rng.integers(40, 220, size=(NUM_SEEDS, 3), dtype=np.uint8)
    image = palette[labels]
    Image.fromarray(image).save(LESSONS_DIR / "3.3.4" / "voronoi.png")
    print("wrote 3.3.4/voronoi.png")


def gen_voronoi_outlined():
    """3.3.4 — Voronoi diagram with cell outlines."""
    SIZE = 400
    NUM_SEEDS = 18
    rng = np.random.default_rng(42)

    seeds = rng.integers(0, SIZE, size=(NUM_SEEDS, 2))
    y, x = np.indices((SIZE, SIZE))
    dy = y[..., None] - seeds[:, 0]
    dx = x[..., None] - seeds[:, 1]
    dist_sq = dy * dy + dx * dx
    labels = np.argmin(dist_sq, axis=-1)

    palette = rng.integers(40, 220, size=(NUM_SEEDS, 3), dtype=np.uint8)
    image = palette[labels]

    up = labels != np.pad(labels[:-1], ((1, 0), (0, 0)), mode="edge")
    down = labels != np.pad(labels[1:], ((0, 1), (0, 0)), mode="edge")
    left = labels != np.pad(labels[:, :-1], ((0, 0), (1, 0)), mode="edge")
    right = labels != np.pad(labels[:, 1:], ((0, 0), (0, 1)), mode="edge")
    borders = up | down | left | right

    image[borders] = [0, 0, 0]
    Image.fromarray(image).save(LESSONS_DIR / "3.3.4" / "voronoi_outlined.png")
    print("wrote 3.3.4/voronoi_outlined.png")


if __name__ == "__main__":
    gen_multiply_demo()
    gen_blend_modes_grid()
    gen_voronoi()
    gen_voronoi_outlined()
    print("done")
