import numpy as np
from PIL import Image

image = np.array(Image.open('source_image.png'))
H, W = image.shape[:2]
mid_y, mid_x = H // 2, W // 2

# TODO 1: slice into four quadrants.
# tl = image[..., ...]
# tr = ...
# bl = ...
# br = ...

# TODO 2: reassemble in scrambled order.
#         Each quadrant must appear exactly once.
# scrambled = np.vstack([
#     np.hstack([?, ?]),
#     np.hstack([?, ?]),
# ])

# TODO 3: verify the *non-scrambled* reassembly matches the original.
# correct = np.vstack([np.hstack([tl, tr]), np.hstack([bl, br])])
# assert np.array_equal(image, correct), 'reassembly does not match'

Image.fromarray(scrambled).save('shuffled_puzzle.png')
