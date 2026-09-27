import numpy as np
from PIL import Image

H, W = 200, 200
source = np.zeros((H, W, 3), dtype=np.uint8)

# Background: diagonal three-colour stripes
y, x = np.ogrid[:H, :W]
stripe = ((x + y) // 20 % 3)
source[(stripe == 0)[0]] = [50, 100, 200]    # ← careful, stripe is broadcast
source[(stripe == 1)[0]] = [100, 200, 100]
source[(stripe == 2)[0]] = [200, 80, 150]

# Orange disc on top
disc = (x - W // 2) ** 2 + (y - H // 2) ** 2 < 60 ** 2
source[disc] = [255, 150, 50]

# TODO 1: build the (H*2, W*2, 3) canvas.
# TODO 2: pick three permutations besides the original and place them in the
#         four quadrants. At least one should be a rotation; at least one a swap.

Image.fromarray(canvas).save('my_warhol.png')
