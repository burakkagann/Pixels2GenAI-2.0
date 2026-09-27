import numpy as np
from PIL import Image

def smoothstep(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def value_noise(shape, scale, seed=0):
    h, w = shape
    rng = np.random.default_rng(seed)
    cells = rng.random((int(np.ceil(h/scale)) + 2, int(np.ceil(w/scale)) + 2))
    y, x = np.mgrid[:h, :w].astype(float)
    yf = y/scale; xf = x/scale
    y0 = yf.astype(int); x0 = xf.astype(int)
    ty = smoothstep(yf - y0); tx = smoothstep(xf - x0)
    c00 = cells[y0, x0];     c10 = cells[y0+1, x0]
    c01 = cells[y0, x0+1];   c11 = cells[y0+1, x0+1]
    top = c00 + (c01 - c00) * tx; bot = c10 + (c11 - c10) * tx
    return top + (bot - top) * ty

def fbm(shape, scale, octaves=5, persistence=0.5, seed=0):
    out = 0; amp = 1.0; s = scale; norm = 0
    for o in range(octaves):
        out = out + amp * value_noise(shape, s, seed + o)
        norm += amp; amp *= persistence; s /= 2
    return out / norm

H, W = 320, 640
z = fbm((H, W), scale=110, octaves=5, seed=42)

sky_top = np.array([0.30, 0.50, 0.85])
sky_bot = np.array([0.80, 0.90, 1.00])
yy = np.linspace(0, 1, H)[:, None, None]
sky = sky_top * (1 - yy) + sky_bot * yy
sky = np.broadcast_to(sky, (H, W, 3)).copy()

cloud = np.clip((z - 0.45) * 4, 0, 1)
out = sky * (1 - cloud[..., None]) + cloud[..., None] * 1.0
rgb = (np.clip(out, 0, 1) * 255).astype(np.uint8)
Image.fromarray(rgb).save('blue_clouds.png')
