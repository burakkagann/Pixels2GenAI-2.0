import numpy as np
from PIL import Image

def vignette(image, strength=1.0):
    H, W, _ = image.shape
    yy, xx = np.mgrid[:H, :W]
    cy, cx = H // 2, W // 2
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    max_dist = np.sqrt(cx ** 2 + cy ** 2)
    norm = dist / max_dist
    brightness = np.clip(1.0 - strength * norm, 0, 1)
    out = image.astype(np.float32) * brightness[..., None]
    return out.clip(0, 255).astype(np.uint8)

a = np.array(Image.open('python_logo.png').convert('RGB'))
Image.fromarray(vignette(a, strength=0.85)).save('vignette.png')
