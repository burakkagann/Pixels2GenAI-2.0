import numpy as np
from PIL import Image

def hue_to_rgb(hue):
    h6 = hue * 6
    c = np.ones_like(h6); z = np.zeros_like(h6)
    x = 1 - np.abs((h6 % 2) - 1)
    seg = h6.astype(int)
    r = np.choose(seg % 6, [c, x, z, z, x, c])
    g = np.choose(seg % 6, [x, c, c, x, z, z])
    b = np.choose(seg % 6, [z, z, x, c, c, x])
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)

H, W = 512, 512
cx, cy = W // 2, H // 2

y, x = np.ogrid[:H, :W]
rel_x = x - cx
rel_y = y - cy
distance = np.sqrt(rel_x ** 2 + rel_y ** 2)
distance[distance == 0] = 1

dx_rot, dy_rot = -rel_y, rel_x
dx_rad = -rel_x / distance
dy_rad = -rel_y / distance

w_rot, w_rad = 0.7, 0.3
dx = w_rot * dx_rot + w_rad * dx_rad * distance
dy = w_rot * dy_rot + w_rad * dy_rad * distance

angle = np.arctan2(dy, dx)
hue = (angle + np.pi) / (2 * np.pi)
rgb = hue_to_rgb(np.broadcast_to(hue, (H, W)))

Image.fromarray(rgb, mode='RGB').save('vortex_field.png')
