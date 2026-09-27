import numpy as np
from PIL import Image

image = np.array(Image.open('bbtor.jpg'))   # any RGB photo will do
h, w = image.shape[:2]

# Grid of pixel coordinates
Y, X = np.ogrid[:h, :w]

# Distance² from the image centre — cheap because we never sqrt
cx, cy = w / 2, h / 2
distance_sq = (X - cx) ** 2 + (Y - cy) ** 2

# Mask: True where the pixel is *outside* the circle
outside = distance_sq > (w * h) / 6

# Blacken every "outside" pixel
image[outside] = 0

Image.fromarray(image).save('mask.png')
