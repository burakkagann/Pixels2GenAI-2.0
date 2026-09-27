import numpy as np
from PIL import Image

def draw_fractal_square(canvas, x_min, x_max, y_min, y_max, depth):
    # Divide the region into a 3x3 grid
    x_third = (x_max - x_min) // 3
    y_third = (y_max - y_min) // 3

    # Locate the center square within the grid
    center_x_start = x_min + x_third
    center_x_end   = x_min + 2 * x_third
    center_y_start = y_min + y_third
    center_y_end   = y_min + 2 * y_third

    # Fill the center square with green (+32 per recursion level)
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    # Recurse into the four corner regions until depth reaches 0
    if depth > 0:
        draw_fractal_square(canvas, x_min,          center_x_end, y_min,          center_y_end, depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max,        y_min,          center_y_end, depth - 1)
        draw_fractal_square(canvas, x_min,          center_x_end, center_y_start, y_max,        depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max,        center_y_start, y_max,        depth - 1)

canvas = np.zeros((800, 800, 3), dtype=np.uint8)
draw_fractal_square(canvas, 0, 800, 0, 800, 3)
Image.fromarray(canvas).save("quickstart_fractal.png")
