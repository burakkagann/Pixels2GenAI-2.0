import numpy as np
from PIL import Image

photo = np.array(Image.open('bbtor.jpg'))
sky = photo[:, :, 2] > 180

# Warm grey-orange outside the subject; white inside
shadow = np.full(photo.shape, [220, 160, 120], dtype=np.uint8)
shadow[sky] = [255, 255, 255]

# Translate the silhouette by 30 px down-and-right
shadow[30:, 30:] = shadow[:-30, :-30]

# Composite back into the original photo, sky-only
photo[sky] = shadow[sky]

Image.fromarray(photo).save('warm_shadow.png')
