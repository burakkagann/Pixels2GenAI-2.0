import numpy as np
from PIL import Image

# ... hue_to_rgb helper from quick start ...

H, W = 512, 512
cx, cy = W // 2, H // 2

y, x = np.ogrid[:H, :W]
rel_x = x - cx
rel_y = y - cy

distance = np.sqrt(rel_x ** 2 + rel_y ** 2)
distance[distance == 0] = 1     # avoid 0/0 at the centre

# TODO 1: build the rotational component (perpendicular to radial)
# dx_rot, dy_rot = ...

# TODO 2: build the *normalised* radial inward component
# dx_rad = -rel_x / distance
# dy_rad = -rel_y / distance

# TODO 3: combine with 70% rotation and 30% radial. Multiply the radial
# part by `distance` in the sum so the rotation dominates near the centre.

# TODO 4: compute angle = arctan2(dy_combined, dx_combined),
# then hue and RGB as in the quick start.

Image.fromarray(rgb, mode='RGB').save('vortex_field.png')
