import numpy as np
from PIL import Image

# Discrete color palette (values divisible by 32)
color_palette = np.array([0, 32, 64, 96, 128, 160, 192, 224])

# TODO 1: Create a 16x16 grid of random indices into the palette
#         (each index selects one of the 8 palette values, for each of 3 channels)

# TODO 2: Map the random indices to actual color values using array indexing

# TODO 3: Scale up to 12x12 pixel tiles using the Kronecker product and save as
#         'richter_style.png'
