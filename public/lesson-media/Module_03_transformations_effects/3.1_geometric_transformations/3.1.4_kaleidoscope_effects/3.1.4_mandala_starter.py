import numpy as np
from PIL import Image

SIZE = 512
CENTER = SIZE // 2

def ring(num_folds, inner_r, outer_r, color_scheme):
    """Return (ring_pixels, mask). Caller composites into the final canvas."""
    y, x = np.ogrid[:SIZE, :SIZE]
    dx, dy = x - CENTER, y - CENTER
    angle = np.arctan2(dy, dx)
    radius = np.sqrt(dx * dx + dy * dy)

    wedge_angle = 2 * np.pi / num_folds
    angle_pos = angle + np.pi
    wedge_idx = (angle_pos / wedge_angle).astype(int)
    angle_in_wedge = angle_pos - wedge_idx * wedge_angle
    is_odd = wedge_idx % 2 == 1
    angle_m = np.where(is_odd, wedge_angle - angle_in_wedge, angle_in_wedge)

    in_ring = (radius >= inner_r) & (radius < outer_r)

    r_mult, g_mult, b_mult = color_scheme
    ring_pos = (radius - inner_r) / max(outer_r - inner_r, 1)
    r = ((np.sin(angle_m * num_folds + ring_pos * np.pi * 2) + 1) * 100 * r_mult + 30).astype(np.uint8)
    g = ((np.cos(angle_m * (num_folds + 2))                    + 1) * 100 * g_mult + 30).astype(np.uint8)
    b = ((np.sin(ring_pos * np.pi * 3)                          + 1) * 100 * b_mult + 30).astype(np.uint8)

    out = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    out[in_ring, 0] = r[in_ring]
    out[in_ring, 1] = g[in_ring]
    out[in_ring, 2] = b[in_ring]
    return out, in_ring

canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

# TODO 1: choose ring specs (inner_r, outer_r, num_folds, color_scheme)
# rings = [...]

# TODO 2: composite each ring into canvas using its mask
# for spec in rings:
#     r, m = ring(*spec)
#     canvas[m] = r[m]

Image.fromarray(canvas).save('mandala.png')
