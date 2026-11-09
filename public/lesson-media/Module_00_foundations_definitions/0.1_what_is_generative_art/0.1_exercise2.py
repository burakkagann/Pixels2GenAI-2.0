"""
A grid of nested squares with a dial for disorder, written after Vera Molnar's
idea of adding a small, controlled amount of disorder to an ordered structure.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image, ImageDraw

# ========== CONFIG: change these values ==========
DISORDER = 0.02      # How far corners may stray: 0 = none, 1 = a whole cell
GRID_SIZE = 8        # Cells along each side of the canvas
NESTED_SQUARES = 5   # Squares drawn inside each cell
SEED = 1974          # Same seed, same drawing. Change it for a new one
# =================================================

CANVAS = 800
cell_size = CANVAS / GRID_SIZE
random_numbers = np.random.default_rng(SEED)

image = Image.new("L", (CANVAS, CANVAS), 255)
draw = ImageDraw.Draw(image)

for row in range(GRID_SIZE):
    for column in range(GRID_SIZE):
        centre_x = (column + 0.5) * cell_size
        centre_y = (row + 0.5) * cell_size

        for square in range(1, NESTED_SQUARES + 1):
            half_side = 0.45 * cell_size * square / NESTED_SQUARES

            # The rule is fixed. Only the corners carry the randomness, which is
            # why a small DISORDER still reads as a grid.
            corners = []
            for x_sign, y_sign in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                stray_x, stray_y = random_numbers.uniform(-1, 1, 2) * DISORDER * cell_size
                corners.append((centre_x + x_sign * half_side + stray_x,
                                centre_y + y_sign * half_side + stray_y))
            draw.polygon(corners, outline=20)

image.save("order_and_disorder.png")
print(f"DISORDER = {DISORDER}, saved as order_and_disorder.png")
