import numpy as np
from PIL import Image

H, W = 200, 200

# A radial sinusoid source — three channels phase-offset
y, x = np.ogrid[:H, :W]
cx, cy = W // 2, H // 2
dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)

source = np.zeros((H, W, 3), dtype=np.uint8)
source[..., 0] = (128 + 127 * np.sin(dist * 0.1)        ).astype(np.uint8)
source[..., 1] = (128 + 127 * np.sin(dist * 0.1 + 2)    ).astype(np.uint8)
source[..., 2] = (128 + 127 * np.sin(dist * 0.1 + 4)    ).astype(np.uint8)

# Four different channel permutations placed in a 2×2 canvas
canvas = np.zeros((H * 2, W * 2, 3), dtype=np.uint8)
canvas[0:H,  0:W ] = source[:, :, [0, 1, 2]]   # original
canvas[0:H,  W: ] = source[:, :, [1, 2, 0]]   # rotate left:  RGB → GBR
canvas[H:,   0:W ] = source[:, :, [2, 0, 1]]   # rotate right: RGB → BRG
canvas[H:,   W: ] = source[:, :, [0, 2, 1]]   # swap G ↔ B

Image.fromarray(canvas).save('simple_warhol.png')
