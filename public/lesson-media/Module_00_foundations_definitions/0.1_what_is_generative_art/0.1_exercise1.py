"""
Fifty points, connected.

A short program that carries out a written instruction: the one Sol LeWitt wrote
for Wall Drawing #118 (1971). This is a coding exercise, not a LeWitt work.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 1000, 500

# No seed on purpose: every run gets new numbers, so every run makes a new drawing.
random_numbers = np.random.default_rng()

# "Evenly distributed" is left to whoever carries out the instruction.
# This program's reading: split the wall into 50 equal cells, one point in each.
columns, rows = 10, 5
points = []
for column in range(columns):
    for row in range(rows):
        x = (column + random_numbers.random()) * WIDTH / columns
        y = (row + random_numbers.random()) * HEIGHT / rows
        points.append((x, y))

# "All of the points should be connected": one straight line for every pair.
wall = Image.new("L", (WIDTH, HEIGHT), 245)
pencil = ImageDraw.Draw(wall)
line_count = 0
for first in range(len(points)):
    for second in range(first + 1, len(points)):
        pencil.line([points[first], points[second]], fill=70, width=1)
        line_count += 1

wall.save("fifty_points.png")
print(f"{len(points)} points, {line_count} lines, saved as fifty_points.png")
