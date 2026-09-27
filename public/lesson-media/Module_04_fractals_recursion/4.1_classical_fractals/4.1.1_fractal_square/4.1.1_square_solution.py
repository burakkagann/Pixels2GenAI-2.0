import numpy as np
from PIL import Image

canvas = np.zeros((800, 800, 3), dtype=np.uint8)

def square(canvas, x_min, x_max, y_min, y_max, depth):
    center_x_start = x_min + (x_max - x_min) // 3
    center_x_end   = x_min + (x_max - x_min) * 2 // 3
    center_y_start = y_min + (y_max - y_min) // 3
    center_y_end   = y_min + (y_max - y_min) * 2 // 3

    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    if depth > 0:
        square(canvas, x_min,          center_x_end, y_min,          center_y_end, depth - 1)  # Top-left
        square(canvas, x_min,          center_x_end, center_y_start, y_max,        depth - 1)  # Bottom-left
        square(canvas, center_x_start, x_max,        y_min,          center_y_end, depth - 1)  # Top-right
        square(canvas, center_x_start, x_max,        center_y_start, y_max,        depth - 1)  # Bottom-right

square(canvas, 0, 800, 0, 800, 3)
Image.fromarray(canvas).save("exercise3_fractal.png")
