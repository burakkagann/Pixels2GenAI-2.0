import numpy as np
from PIL import Image

photo = np.array(Image.open('bbtor.jpg'))
sky = photo[:, :, 2] > 180

# TODO 1: build a 3-channel shadow layer where the *base* colour is warm
#         (e.g. (220, 160, 120)) and the in-subject region is white.

# TODO 2: translate the whole layer by (30, 30) using slice assignment on all 3 channels.

# TODO 3: composite back into photo *inside the sky mask only*.

Image.fromarray(photo).save('warm_shadow.png')
