import numpy as np
from PIL import Image

CANVAS_SIZE = 400
NUM_STARS = 150

canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

# Uniformly random (x, y) for each star
x_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)
y_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)

# Integer array indexing — paint all 150 pixels in one assignment
canvas[y_coords, x_coords] = 255

Image.fromarray(canvas, mode='L').save('simple_star.png')
