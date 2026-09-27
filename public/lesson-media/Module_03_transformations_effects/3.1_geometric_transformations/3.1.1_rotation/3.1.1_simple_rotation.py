import numpy as np
from scipy import ndimage
from PIL import Image

canvas_size = 400
image = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# A cyan rectangle, centred horizontally
image[150:250, 100:300] = [0, 200, 200]

rotated = ndimage.rotate(image, 45, reshape=False, mode='constant', cval=0)

# Side-by-side: original on the left, rotated on the right
comparison = np.zeros((canvas_size, canvas_size * 2 + 20, 3), dtype=np.uint8)
comparison[:, :canvas_size] = image
comparison[:, canvas_size + 20:] = rotated

Image.fromarray(comparison).save('simple_rotation.png')
