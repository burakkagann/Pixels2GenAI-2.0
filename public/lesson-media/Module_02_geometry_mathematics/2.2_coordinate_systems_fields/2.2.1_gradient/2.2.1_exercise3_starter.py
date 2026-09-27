import numpy as np
from PIL import Image

size = 400

# TODO 1: build a horizontal 1D linspace from 0 to 255 with `size` values
# horizontal = ...

# TODO 2: build a vertical column vector with the same values
# vertical = ...

# TODO 3: combine them via broadcasting; divide by 2 to stay in [0, 255]
# diagonal = ...

# TODO 4: cast to uint8 before saving
# gradient_image = ...

Image.fromarray(gradient_image, mode='L').save('diagonal_gradient.png')
