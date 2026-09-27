import numpy as np
from PIL import Image

H, W = 256, 256
image = np.zeros((H, W), dtype=np.float64)

# TODO 1: draw your pattern. Example: a "T" shape using rectangles.

# TODO 2: define Gx and Gy (you know what these are now).
# Gx = ...
# Gy = ...

# TODO 3: convolve and compute magnitude in nested loops.

# TODO 4: normalise to [0, 255] and save.

Image.fromarray(...).save('my_edges.png')
