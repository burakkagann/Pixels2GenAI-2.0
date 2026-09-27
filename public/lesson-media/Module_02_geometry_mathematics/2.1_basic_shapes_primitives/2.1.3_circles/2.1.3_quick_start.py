import numpy as np
from PIL import Image

CANVAS_SIZE = 512
CENTER_X, CENTER_Y = 256, 256
RADIUS = 150
CIRCLE_COLOR = [255, 128, 0]   # orange

# Open coordinate grids — Y is (512, 1), X is (1, 512)
Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]

# Squared distance from centre for every pixel
square_distance = (X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2

# Boolean mask of pixels inside the circle
inside_circle = square_distance < RADIUS ** 2

canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)
canvas[inside_circle] = CIRCLE_COLOR

Image.fromarray(canvas, mode='RGB').save('circle.png')
