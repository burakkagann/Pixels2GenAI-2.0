import numpy as np
from PIL import Image

def hue_to_rgb(hue):
    """Map an array of hue values in [0, 1] to RGB via the standard 6-segment wheel."""
    h6 = hue * 6
    c = np.ones_like(h6)
    x = 1 - np.abs((h6 % 2) - 1)
    z = np.zeros_like(h6)
    seg = h6.astype(int)
    r = np.choose(seg % 6, [c, x, z, z, x, c])
    g = np.choose(seg % 6, [x, c, c, x, z, z])
    b = np.choose(seg % 6, [z, z, x, c, c, x])
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)

H, W = 512, 512
cx, cy = W // 2, H // 2

y, x = np.ogrid[:H, :W]
dx = cx - x           # vector pointing toward centre
dy = cy - y

angle = np.arctan2(dy, dx)                  # in [-pi, pi]
hue = (angle + np.pi) / (2 * np.pi)         # in [0, 1]
rgb = hue_to_rgb(np.broadcast_to(hue, (H, W)))

Image.fromarray(rgb, mode='RGB').save('simple_vector_field.png')
