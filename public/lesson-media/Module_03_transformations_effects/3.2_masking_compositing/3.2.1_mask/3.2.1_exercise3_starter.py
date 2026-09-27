import numpy as np
from PIL import Image

image = np.array(Image.open('bbtor.jpg'))
h, w = image.shape[:2]

# Normalise coordinates so the heart can be tuned in (−1, 1)
Y, X = np.ogrid[:h, :w]
nx = (X - w / 2) / (w / 2)
ny = (Y - h / 2) / (h / 2)
ny = -ny     # flip y so the heart points "up" on screen

# TODO 1: build the heart mask. Two starter routes — pick one.
# Algebraic curve:
#   (x² + y² − 1)³ − x² · y³ < 0  is the inside of a heart.
# Or: two circles for the lobes + a downward triangle for the point.

# TODO 2: blacken everything *outside* the heart.

Image.fromarray(image).save('heart_mask.png')
