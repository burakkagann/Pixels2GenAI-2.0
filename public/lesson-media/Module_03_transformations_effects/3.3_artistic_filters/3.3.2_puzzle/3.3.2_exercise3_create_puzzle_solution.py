import numpy as np
from PIL import Image

image = np.array(Image.open('source_image.png'))
H, W = image.shape[:2]
mid_y, mid_x = H // 2, W // 2

tl = image[:mid_y, :mid_x]
tr = image[:mid_y, mid_x:]
bl = image[mid_y:, :mid_x]
br = image[mid_y:, mid_x:]

# Verify correct order rebuilds the original
correct = np.vstack([np.hstack([tl, tr]), np.hstack([bl, br])])
assert np.array_equal(image, correct), 'reassembly does not match'

# Artistic shuffle
scrambled = np.vstack([
    np.hstack([br, tl]),
    np.hstack([tr, bl]),
])

Image.fromarray(scrambled).save('shuffled_puzzle.png')
