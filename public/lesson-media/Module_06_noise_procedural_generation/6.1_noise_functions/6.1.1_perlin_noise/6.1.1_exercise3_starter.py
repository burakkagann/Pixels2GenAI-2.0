import numpy as np
from PIL import Image

# Noise functions from value_clouds.py (the quick start), unchanged
def smoothstep(t):
    return t * t * t * (t * (t * 6 - 15) + 10)        # quintic, Perlin 2002

def value_noise(shape, scale, seed=0):
    h, w = shape
    rng = np.random.default_rng(seed)
    cells_y = int(np.ceil(h / scale)) + 2
    cells_x = int(np.ceil(w / scale)) + 2
    cells = rng.random((cells_y, cells_x))            # random per grid corner

    y, x = np.mgrid[:h, :w].astype(np.float64)
    yf = y / scale; xf = x / scale
    y0 = yf.astype(int); x0 = xf.astype(int)
    ty = smoothstep(yf - y0)
    tx = smoothstep(xf - x0)

    c00 = cells[y0,     x0    ]; c10 = cells[y0 + 1, x0    ]
    c01 = cells[y0,     x0 + 1]; c11 = cells[y0 + 1, x0 + 1]
    top = c00 + (c01 - c00) * tx
    bot = c10 + (c11 - c10) * tx
    return top + (bot - top) * ty                     # in [0, 1]

def fbm(shape, scale, octaves=6, persistence=0.5, seed=0):
    out = np.zeros(shape); amp = 1.0; s = scale; norm = 0
    for o in range(octaves):
        out += amp * value_noise(shape, s, seed + o)
        norm += amp; amp *= persistence; s /= 2
    return out / norm

H, W = 320, 640
z = fbm((H, W), scale=110, octaves=5, seed=42)

# TODO 1: build a sky gradient — RGB that goes from a deep blue at top
#         to a paler blue at the horizon.

# TODO 2: build a cloud overlay: white where z is high, transparent where low.
#         Multiply-screen the cloud onto the sky.

Image.fromarray(rgb_uint8).save('blue_clouds.png')
