import numpy as np
from PIL import Image

def draw_filled_triangle(canvas, v1, v2, v3, color):
    h, w = canvas.shape[:2]
    y_coords, x_coords = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')

    def edge(x, y, x1, y1, x2, y2):
        return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

    e1 = edge(x_coords, y_coords, *v1, *v2) <= 0
    e2 = edge(x_coords, y_coords, *v2, *v3) <= 0
    e3 = edge(x_coords, y_coords, *v3, *v1) <= 0
    canvas[e1 & e2 & e3] = color

def create_gradient_sky(h, w):
    sky = np.zeros((h, w, 3), dtype=np.uint8)
    top = np.array([25, 25, 112])
    bot = np.array([255, 140, 50])
    for y in range(h):
        t = y / h
        sky[y, :] = ((1 - t) * top + t * bot).astype(np.uint8)
    return sky

h, w = 400, 500
canvas = create_gradient_sky(h, w)

mountains = [
    {'peak': (400,  80), 'left': (250, 400), 'right': (500, 400), 'color': (100, 100, 120)},
    {'peak': (150, 120), 'left': (0,   400), 'right': (320, 400), 'color': (70,  80,  90)},
    {'peak': (300, 180), 'left': (150, 400), 'right': (480, 400), 'color': (40,  45,  50)},
    {'peak': (80,  250), 'left': (0,   400), 'right': (200, 400), 'color': (30,  35,  40)},
]
for m in mountains:
    draw_filled_triangle(canvas, m['peak'], m['right'], m['left'], m['color'])

Image.fromarray(canvas).save('triangle_mountain.png')
