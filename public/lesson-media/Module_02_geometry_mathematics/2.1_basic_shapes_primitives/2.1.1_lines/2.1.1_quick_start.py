import numpy as np
from PIL import Image

canvas = np.zeros((400, 400), dtype=np.uint8)

# Endpoints in (x, y) pixel coordinates
x_start, y_start = 50, 50
x_end, y_end = 350, 350

# Generate enough sample points to fill every pixel along the longer axis
num_points = max(abs(x_end - x_start), abs(y_end - y_start)) + 1

x_coords = np.linspace(x_start, x_end, num_points).round().astype(int)
y_coords = np.linspace(y_start, y_end, num_points).round().astype(int)

# Array indexing is [row, column] = [y, x]
canvas[y_coords, x_coords] = 255

Image.fromarray(canvas).save('simple_line.png')
