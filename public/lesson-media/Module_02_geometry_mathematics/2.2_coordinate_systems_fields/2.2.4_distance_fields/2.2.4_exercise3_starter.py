import numpy as np
from PIL import Image

SIZE = 512
CENTER = SIZE // 2

Y, X = np.ogrid[0:SIZE, 0:SIZE]
x = X - CENTER
y = Y - CENTER

# TODO 1: outer circle SDF (radius 180)
# outer = np.sqrt(x**2 + y**2) - 180

# TODO 2: inner circle SDF (radius 100)
# inner = np.sqrt(x**2 + y**2) - 100

# TODO 3: ring = outer minus inner (use np.maximum and negation)
# ring = np.maximum(outer, -inner)

# TODO 4: vertical rectangle SDF — half-width 30, half-height 200
# rect = np.maximum(np.abs(x) - 30, np.abs(y) - 200)

# TODO 5: union the ring and the rectangle (np.minimum)
# combined = np.minimum(ring, rect)

# Visualisation: clip to [-150, 150], shift to [0, 300], scale to [0, 255]
# normalized = np.clip(combined, -150, 150)
# normalized = ((normalized + 150) / 300 * 255).astype(np.uint8)
# Image.fromarray(normalized, mode='L').save('sdf_combination.png')
