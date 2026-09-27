import numpy as np
from PIL import Image

img = np.array(Image.open('bbtor.jpg').convert('L'), dtype=np.float64)
H, W = img.shape

F = np.fft.fft2(img)
F_shift = np.fft.fftshift(F)

y, x = np.indices((H, W))
cx, cy = W // 2, H // 2
dist_sq = (x - cx) ** 2 + (y - cy) ** 2

mask = np.zeros((H, W), dtype=np.float64)
left  = x <  cx
right = x >= cx
mask[left]  = (dist_sq <= 40 ** 2)[left]
mask[right] = (dist_sq >  40 ** 2)[right]

rng = np.random.default_rng(0)
for _ in range(5):
    y0 = rng.integers(0, H - 20); x0 = rng.integers(0, W - 20)
    h  = rng.integers(5, 20);     w  = rng.integers(5, 20)
    mask[y0:y0 + h, x0:x0 + w] = 0

F_filt = F_shift * mask
result = np.real(np.fft.ifft2(np.fft.ifftshift(F_filt)))
glitched = np.clip(result, 0, 255).astype(np.uint8)

side_by_side = np.hstack([img.astype(np.uint8), glitched])
Image.fromarray(side_by_side, 'L').save('glitch.png')
