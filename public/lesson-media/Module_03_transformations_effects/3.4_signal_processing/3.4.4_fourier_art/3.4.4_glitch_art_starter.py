import numpy as np
from PIL import Image

img = np.array(Image.open('bbtor.jpg').convert('L'), dtype=np.float64)
H, W = img.shape

F = np.fft.fft2(img)
F_shift = np.fft.fftshift(F)

# TODO 1: build an asymmetric mask — different rule for x < W/2 vs x >= W/2.

# TODO 2: poke 5 random rectangular "glitch holes" by zeroing regions of the mask.
rng = np.random.default_rng(0)

# TODO 3: apply, inverse-transform, take real part, clip, save side-by-side.

Image.fromarray(np.hstack([img, glitched]).astype(np.uint8), 'L').save('glitch.png')
