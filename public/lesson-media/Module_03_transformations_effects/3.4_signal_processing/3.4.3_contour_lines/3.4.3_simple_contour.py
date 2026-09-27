import numpy as np
from PIL import Image

SIZE = 300

x = np.linspace(-5, 5, SIZE)
y = np.linspace(-5, 5, SIZE)
X, Y = np.meshgrid(x, y)

# A single Gaussian hill centred at origin
height = np.exp(-(X**2 + Y**2) / 4)

# Normalise to [0, 1], quantise into 8 levels, rescale to [0, 255]
normalised = (height - height.min()) / (height.max() - height.min())
contour = (normalised * 8).astype(np.uint8) * 32     # 8 × 32 = 256 → wraps to 0
contour = np.clip(contour, 0, 255).astype(np.uint8)

Image.fromarray(contour, 'L').save('simple_contour.png')
