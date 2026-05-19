"""
Fractal Square

Generates a self-similar fractal pattern by recursively subdividing a square
into a 3x3 grid, filling the center, and repeating on the four corner regions.
Color accumulates where regions overlap, revealing the recursive structure
through brightness variation.

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


def draw_fractal_square(canvas, x_min, x_max, y_min, y_max, depth):
    # Divide the region into a 3x3 grid by calculating thirds
    x_third = (x_max - x_min) // 3
    y_third = (y_max - y_min) // 3

    # Locate the center square boundaries
    center_x_start = x_min + x_third
    center_x_end = x_min + 2 * x_third
    center_y_start = y_min + y_third
    center_y_end = y_min + 2 * y_third

    # Fill the center square by adding 32 to the green channel
    # The += operator accumulates color where regions overlap
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    # Recurse into the four corner regions until depth reaches 0
    if depth > 0:
        # Top-left corner
        draw_fractal_square(canvas, x_min, center_x_end, y_min, center_y_end, depth - 1)
        # Top-right corner
        draw_fractal_square(canvas, center_x_start, x_max, y_min, center_y_end, depth - 1)
        # Bottom-left corner
        draw_fractal_square(canvas, x_min, center_x_end, center_y_start, y_max, depth - 1)
        # Bottom-right corner
        draw_fractal_square(canvas, center_x_start, x_max, center_y_start, y_max, depth - 1)


# Create an 800x800 black canvas with 3 color channels (RGB)
canvas_size = 800
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Generate the fractal with 3 levels of recursion
recursion_depth = 3
draw_fractal_square(canvas, 0, canvas_size, 0, canvas_size, recursion_depth)

# Save the result as a PNG image
image = Image.fromarray(canvas)
image.save("exercise1_fractal.png")
print(f"Saved exercise1_fractal.png ({canvas_size}x{canvas_size}, depth={recursion_depth})")
