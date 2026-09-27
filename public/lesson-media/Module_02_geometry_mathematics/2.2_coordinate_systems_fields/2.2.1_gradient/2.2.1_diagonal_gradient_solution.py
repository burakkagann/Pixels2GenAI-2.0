import numpy as np
from PIL import Image

size = 400

horizontal = np.linspace(0, 255, size)
vertical = np.linspace(0, 255, size).reshape(-1, 1)

diagonal = (horizontal + vertical) / 2
gradient_image = diagonal.astype(np.uint8)

Image.fromarray(gradient_image, mode='L').save('diagonal_gradient.png')
