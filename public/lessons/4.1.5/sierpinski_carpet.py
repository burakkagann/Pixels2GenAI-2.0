"""
sierpinski_carpet.py — the square cousin of the Sierpinski triangle. At each
depth, the current square is divided into a 3x3 grid and the centre cell is
removed; the eight surrounding cells recurse. The result is the Sierpinski
carpet, with fractal dimension log(8)/log(3) ~= 1.893.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 729  # 3^6 — keeps every recursion exactly aligned to integer pixels


def carve_carpet(canvas, x, y, side, depth, color):
    """Fill an entire square, then recurse to carve eight corner sub-squares."""
    if depth == 0:
        canvas[y:y + side, x:x + side] = color
        return

    third = side // 3
    # Recurse into 8 sub-squares, skipping the centre.
    for dy in range(3):
        for dx in range(3):
            if dy == 1 and dx == 1:
                continue
            carve_carpet(canvas, x + dx * third, y + dy * third, third, depth - 1, color)


canvas = np.full((SIZE, SIZE, 3), [20, 20, 30], dtype=np.uint8)
carve_carpet(canvas, 0, 0, SIZE, depth=5, color=np.array([110, 200, 255], dtype=np.uint8))

Image.fromarray(canvas, mode='RGB').save('sierpinski_carpet.png')
print(f"Saved sierpinski_carpet.png — depth 5, {8 ** 5} solid sub-squares")
