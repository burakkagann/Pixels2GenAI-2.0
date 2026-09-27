import numpy as np
from PIL import Image

size = 400
tile = 50
image = np.zeros((size, size, 3), dtype=np.uint8)
colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
for r in range(size // tile):
    for c in range(size // tile):
        image[r*tile:(r+1)*tile, c*tile:(c+1)*tile] = colors[(r + c) % 4]

h_amp, h_freq = 15, 3
v_amp, v_freq = 15, 4

distorted = np.zeros_like(image)
for y in range(size):
    for x in range(size):
        h_off = int(h_amp * np.sin(2 * np.pi * h_freq * y / size))
        v_off = int(v_amp * np.sin(2 * np.pi * v_freq * x / size))
        source_x = (x + h_off) % size
        source_y = (y + v_off) % size
        distorted[y, x] = image[source_y, source_x]

Image.fromarray(distorted).save('combined_waves.png')
