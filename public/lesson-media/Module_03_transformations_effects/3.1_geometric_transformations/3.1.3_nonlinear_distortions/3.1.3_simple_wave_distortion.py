import numpy as np
from PIL import Image

# Build a small checkerboard so the distortion is easy to see
size = 400
tile = 50
image = np.zeros((size, size, 3), dtype=np.uint8)
colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
for r in range(size // tile):
    for c in range(size // tile):
        image[r*tile:(r+1)*tile, c*tile:(c+1)*tile] = colors[(r + c) % 4]

# Sine-wave horizontal shift — x depends on y
amplitude = 20
frequency = 3
distorted = np.zeros_like(image)
for y in range(size):
    offset = int(amplitude * np.sin(2 * np.pi * frequency * y / size))
    for x in range(size):
        source_x = (x + offset) % size
        distorted[y, x] = image[y, source_x]

Image.fromarray(distorted).save('wave_distortion.png')
