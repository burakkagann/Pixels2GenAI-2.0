import numpy as np
from PIL import Image

SIZE = 256
TILE = 16

# Procedural checkerboard
rows = (np.arange(SIZE) // TILE)[:, None]
cols = (np.arange(SIZE) // TILE)[None, :]
image = np.where((rows + cols) % 2 == 0, 255.0, 0.0)

# Forward FFT, centre the zero-frequency
F = np.fft.fft2(image)
F_shift = np.fft.fftshift(F)

# Log-scaled magnitude spectrum for display
mag = np.log1p(np.abs(F_shift))
mag = (mag / mag.max() * 255).astype(np.uint8)

# Side-by-side: image | spectrum
combo = np.hstack([image.astype(np.uint8), mag])
Image.fromarray(combo, 'L').save('simple_fft_output.png')
