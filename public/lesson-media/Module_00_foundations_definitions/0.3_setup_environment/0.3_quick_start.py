import sys

import numpy as np
from PIL import Image

print(f"Python {sys.version.split()[0]}, NumPy {np.__version__}")

# An image is a grid of numbers. This one holds 256 greys, dark on the left.
gradient = np.linspace(0, 255, 256, dtype=np.uint8)
image = np.tile(gradient, (80, 1))

Image.fromarray(image).save("first_image.png")
print("Saved first_image.png")
