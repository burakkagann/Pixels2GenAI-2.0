import numpy as np
from PIL import Image

size = 400
tile = 50
image = np.zeros((size, size, 3), dtype=np.uint8)
colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
for r in range(size // tile):
    for c in range(size // tile):
        image[r*tile:(r+1)*tile, c*tile:(c+1)*tile] = colors[(r + c) % 4]

# TODO 1: pick amplitude + frequency for both axes (different freqs!)
# h_amp, h_freq = ...
# v_amp, v_freq = ...

distorted = np.zeros_like(image)
for y in range(size):
    for x in range(size):
        # TODO 2: compute h_offset (a function of y) and v_offset (a function of x).
        # TODO 3: combine into source_x and source_y, wrap with % size, and copy.
        pass

Image.fromarray(distorted).save('combined_waves.png')
