import numpy as np
from PIL import Image

H, W = 200, 200
source = np.zeros((H, W, 3), dtype=np.uint8)

y, x = np.ogrid[:H, :W]
stripe = (x + y) // 20 % 3
source[stripe == 0] = [50, 100, 200]
source[stripe == 1] = [100, 200, 100]
source[stripe == 2] = [200, 80, 150]

disc = (x - W // 2) ** 2 + (y - H // 2) ** 2 < 60 ** 2
source[disc] = [255, 150, 50]

canvas = np.zeros((H * 2, W * 2, 3), dtype=np.uint8)
canvas[0:H,  0:W ] = source[:, :, [0, 1, 2]]
canvas[0:H,  W: ] = source[:, :, [1, 2, 0]]
canvas[H:,   0:W ] = source[:, :, [2, 0, 1]]
canvas[H:,   W: ] = source[:, :, [2, 1, 0]]

Image.fromarray(canvas).save('my_warhol.png')
