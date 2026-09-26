import numpy as np
from PIL import Image

size = 512
center = size // 2
num_folds = 6
wedge_angle = 2 * np.pi / num_folds

# Polar coordinates for every pixel
y, x = np.ogrid[:size, :size]
dx, dy = x - center, y - center
angle = np.arctan2(dy, dx)
radius = np.sqrt(dx * dx + dy * dy)

# Fold all angles into one wedge
angle_pos = angle + np.pi                                # shift to [0, 2π)
wedge_idx = (angle_pos / wedge_angle).astype(int)
angle_in_wedge = angle_pos - wedge_idx * wedge_angle

# Mirror odd-numbered wedges
is_odd = wedge_idx % 2 == 1
angle_mirrored = np.where(is_odd, wedge_angle - angle_in_wedge, angle_in_wedge)

# Procedural colours that depend on the folded angle + radius
r_ch = ((np.sin(angle_mirrored * 3 + radius * 0.05) + 1) * 127).astype(np.uint8)
g_ch = ((np.cos(angle_mirrored * 2 + radius * 0.03) + 1) * 80 + 30).astype(np.uint8)
b_ch = ((np.sin(radius * 0.08) + 1) * 100 + 30).astype(np.uint8)

mask = radius <= center - 10
out = np.zeros((size, size, 3), dtype=np.uint8)
out[mask, 0] = r_ch[mask]; out[mask, 1] = g_ch[mask]; out[mask, 2] = b_ch[mask]

Image.fromarray(out).save('simple_kaleidoscope.png')
