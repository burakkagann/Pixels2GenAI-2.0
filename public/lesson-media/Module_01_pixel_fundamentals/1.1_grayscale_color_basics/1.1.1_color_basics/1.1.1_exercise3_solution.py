import numpy as np
from PIL import Image

height, width = 200, 200
image = np.zeros((height, width, 3), dtype=np.uint8)

# Create gradient from red (left) to blue (right)
for col in range(width):
    image[:, col, 0] = 255 - (col * 255 // width)  # Red decreases
    image[:, col, 2] = col * 255 // width          # Blue increases
    # Green channel stays 0

Image.fromarray(image).save('red_to_blue_gradient.png')
