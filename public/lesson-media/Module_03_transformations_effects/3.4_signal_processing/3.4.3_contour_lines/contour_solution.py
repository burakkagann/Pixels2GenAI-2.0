import numpy as np
from PIL import Image

SIZE = 400
N_HILLS = 15
rng = np.random.default_rng(0)

x = np.linspace(-10, 10, SIZE)
y = np.linspace(-10, 10, SIZE)
X, Y = np.meshgrid(x, y)

Z = np.zeros_like(X)
for _ in range(N_HILLS):
    cx, cy = rng.uniform(-9, 9, size=2)
    amp = rng.uniform(0.5, 2.0)
    width = rng.uniform(1.5, 4.0)
    Z = Z + amp * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / width)

znorm = (Z - Z.min()) / (Z.max() - Z.min())

stepped = ((znorm * 8).astype(np.uint8) * 32).clip(0, 255).astype(np.uint8)
isolines = (((znorm * 100).round() % 12) == 0).astype(np.uint8) * 255

Image.fromarray(stepped, 'L').save('random_terrain.png')
Image.fromarray(isolines, 'L').save('random_terrain_isolines.png')
