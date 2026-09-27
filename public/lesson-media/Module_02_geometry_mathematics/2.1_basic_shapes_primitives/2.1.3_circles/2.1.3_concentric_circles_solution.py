import numpy as np
from PIL import Image

CANVAS_SIZE = 512
CENTER_X, CENTER_Y = 256, 256

RADII  = [200, 160, 120, 80, 40]
RED, WHITE = [255, 0, 0], [255, 255, 255]
COLORS = [RED, WHITE, RED, WHITE, RED]

Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]
square_distance = (X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2

canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)
for radius, color in zip(RADII, COLORS):
    canvas[square_distance < radius ** 2] = color

Image.fromarray(canvas, mode='RGB').save('concentric_circles.png')
