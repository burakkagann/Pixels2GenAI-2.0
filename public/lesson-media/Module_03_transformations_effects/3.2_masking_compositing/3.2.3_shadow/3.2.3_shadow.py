import numpy as np
from PIL import Image

photo = np.array(Image.open('bbtor.jpg'))

# 1. Mask: pixels whose blue channel is brighter than 180 (most of the sky)
sky_mask = photo[:, :, 2] > 180

# 2. Silhouette layer: solid grey, with white wherever the subject is
shadow = np.full(photo.shape, 127, dtype=np.uint8)
shadow[sky_mask] = 255

# 3. Translate the silhouette down-and-right by 20 px (in-place via slicing)
shadow[20:, 20:] = shadow[:-20, :-20]

# 4. Paint the translated silhouette back onto the photo, but only in the sky
photo[sky_mask] = shadow[sky_mask]

Image.fromarray(photo, 'RGB').save('shadow.png')
