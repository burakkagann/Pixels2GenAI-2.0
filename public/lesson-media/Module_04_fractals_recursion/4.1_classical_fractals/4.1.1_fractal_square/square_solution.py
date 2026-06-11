"""
Exercise 3: Fractal Square - Complete Solution

Reference solution for the fractal square exercise. Implements the full
recursive subdivision with four corner calls that each cover 2/3 of the
parent region, creating overlapping self-similar patterns.

Implementation inspired by:
- Mandelbrot, B.B. (1982). The Fractal Geometry of Nature. W.H. Freeman.
  Chapter on self-similar fractals and fractional dimensions.
- Barnsley, M.F. (1988). Fractals Everywhere. Academic Press.
  Iterated Function Systems for fractal generation.
- Peitgen, H.-O. & Richter, P.H. (1986). The Beauty of Fractals.
  Springer-Verlag. Visual fractal construction techniques.
- Peitgen, H.-O., Jurgens, H. & Saupe, D. (1992). Fractals for the
  Classroom. Springer/NCTM. Educational fractal exercises and activities.
"""

import numpy as np
from PIL import Image

# Create an 800x800 black canvas with 3 color channels (RGB)
canvas = np.zeros((800, 800, 3), dtype=np.uint8)


def square(canvas, x_min, x_max, y_min, y_max, depth):
    # Calculate grid division points (thirds of the region)
    center_x_start = x_min + (x_max - x_min) // 3
    center_x_end = x_min + (x_max - x_min) * 2 // 3
    center_y_start = y_min + (y_max - y_min) // 3
    center_y_end = y_min + (y_max - y_min) * 2 // 3

    # Fill the center square with green color
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    if depth > 0:
        # Each corner covers 2/3 of the parent region, creating overlap
        square(canvas, x_min, center_x_end, y_min, center_y_end, depth - 1)     # Top-left
        square(canvas, x_min, center_x_end, center_y_start, y_max, depth - 1)   # Bottom-left
        square(canvas, center_x_start, x_max, y_min, center_y_end, depth - 1)   # Top-right
        square(canvas, center_x_start, x_max, center_y_start, y_max, depth - 1) # Bottom-right


# Run the fractal with depth 3 and save the result
square(canvas, 0, 800, 0, 800, depth=3)
image = Image.fromarray(canvas)
image.save("exercise3_fractal.png")
