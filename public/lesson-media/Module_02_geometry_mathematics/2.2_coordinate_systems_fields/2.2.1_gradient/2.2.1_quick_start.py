import numpy as np
from PIL import Image

height, width = 300, 800

# 1D linspace: 800 evenly-spaced values between 0 and 255
gradient_values = np.linspace(0, 255, width, dtype=np.uint8)

# np.tile repeats the row `height` times to fill the canvas
gradient_image = np.tile(gradient_values, (height, 1))

Image.fromarray(gradient_image, mode='L').save('simple_gradient.png')
