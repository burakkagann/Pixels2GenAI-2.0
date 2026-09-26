import numpy as np
from PIL import Image

SIZE = 400
N_HILLS = 15
rng = np.random.default_rng(0)

x = np.linspace(-10, 10, SIZE)
y = np.linspace(-10, 10, SIZE)
X, Y = np.meshgrid(x, y)

Z = np.zeros_like(X)

# TODO 1: for each of N_HILLS, sample random (cx, cy, amplitude, width)
#         and add an exp(-((X-cx)**2 + (Y-cy)**2) / width) term to Z.

# TODO 2: normalise Z to [0, 1].

# TODO 3: save the stepped contour (8 levels) AND the isolines.

Image.fromarray(stepped, 'L').save('random_terrain.png')
Image.fromarray(isolines, 'L').save('random_terrain_isolines.png')
