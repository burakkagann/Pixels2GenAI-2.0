import numpy as np
from PIL import Image

image = np.array(Image.open('bbtor.jpg'))
h, w = image.shape[:2]

Y, X = np.ogrid[:h, :w]
nx = (X - w / 2) / (w / 2)
ny = -((Y - h / 2) / (h / 2))   # flip y

# Algebraic heart curve
heart_inside = (nx**2 + ny**2 - 1) ** 3 - nx**2 * ny**3 < 0

# Blacken outside
image[~heart_inside] = 0

Image.fromarray(image).save('heart_mask.png')
