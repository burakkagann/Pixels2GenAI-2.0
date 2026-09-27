import numpy as np
from PIL import Image

# Create image
height, width = 200, 200
image = np.zeros((height, width, 3), dtype=np.uint8)

# Your code here: fill the image with a gradient.
# Loop over columns and set red and blue channels.

Image.fromarray(image).save('gradient.png')
