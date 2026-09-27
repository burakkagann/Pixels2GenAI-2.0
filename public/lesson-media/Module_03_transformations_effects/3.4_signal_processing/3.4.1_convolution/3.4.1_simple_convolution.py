import numpy as np
from PIL import Image

SIZE = 256
TILE = 32

# Procedural checkerboard with sharp edges
rows = (np.arange(SIZE) // TILE)[:, None]
cols = (np.arange(SIZE) // TILE)[None, :]
canvas = np.where((rows + cols) % 2 == 0, 255.0, 0.0)

K = 5
blur = np.ones((K, K)) / (K * K)            # equal weights, sum to 1

# Convolution by nested loops (valid output: image - kernel + 1)
out_size = SIZE - K + 1
out = np.zeros((out_size, out_size))
for y in range(out_size):
    for x in range(out_size):
        region = canvas[y:y + K, x:x + K]
        out[y, x] = np.sum(region * blur)

# Side by side: the original (cropped to the same size) | grey gap | the blur
half = K // 2
original = canvas[half:-half, half:-half]
gap = np.full((out_size, 10), 128.0)
side_by_side = np.hstack([original, gap, out])
Image.fromarray(side_by_side.astype(np.uint8), 'L').save('simple_convolution.png')
