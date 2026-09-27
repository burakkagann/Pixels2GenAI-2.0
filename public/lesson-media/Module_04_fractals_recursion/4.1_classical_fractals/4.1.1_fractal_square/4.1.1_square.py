"""
Exercise 3: Fractal Square - Starter Code

Complete the recursive calls in the square() function to generate the
fractal pattern. The center square filling is provided; you need to add
the four corner recursive calls.

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
    # Calculate the one-third and two-thirds marks along x-axis
    center_x_start = x_min + (x_max - x_min) // 3
    center_x_end = x_min + (x_max - x_min) * 2 // 3
    # Calculate the one-third and two-thirds marks along y-axis
    center_y_start = y_min + (y_max - y_min) // 3
    center_y_end = y_min + (y_max - y_min) * 2 // 3

    # Fill the center square with green color
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    if depth > 0:
        # TODO: Add four recursive calls for each corner region
        square(canvas, ..., ..., ..., ..., depth - 1)
        ...


# Run the fractal with depth 1 and save the result
square(canvas, 0, 800, 0, 800, depth=1)
image = Image.fromarray(canvas)
image.save("exercise3_fractal.png")
