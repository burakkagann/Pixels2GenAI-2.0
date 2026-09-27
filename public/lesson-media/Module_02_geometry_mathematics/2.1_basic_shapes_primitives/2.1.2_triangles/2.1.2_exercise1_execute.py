import numpy as np
from PIL import Image

height, width = 400, 400
y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

v1, v2, v3 = (200, 50), (350, 350), (50, 350)

def edge(x, y, x1, y1, x2, y2):
    return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

e1 = edge(x_coords, y_coords, *v1, *v2) <= 0
e2 = edge(x_coords, y_coords, *v2, *v3) <= 0
e3 = edge(x_coords, y_coords, *v3, *v1) <= 0
mask = e1 & e2 & e3

canvas = np.zeros((height, width), dtype=np.uint8)
canvas[mask] = 255
Image.fromarray(canvas).save('simple_triangle.png')
