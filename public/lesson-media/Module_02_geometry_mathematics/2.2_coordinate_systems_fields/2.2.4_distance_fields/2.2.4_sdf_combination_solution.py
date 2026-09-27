import numpy as np
from PIL import Image

SIZE = 512
CENTER = SIZE // 2

Y, X = np.ogrid[0:SIZE, 0:SIZE]
x = X - CENTER
y = Y - CENTER

outer = np.sqrt(x ** 2 + y ** 2) - 180
inner = np.sqrt(x ** 2 + y ** 2) - 100
ring  = np.maximum(outer, -inner)

rect = np.maximum(np.abs(x) - 30, np.abs(y) - 200)

combined = np.minimum(ring, rect)

normalized = np.clip(combined, -150, 150)
normalized = ((normalized + 150) / 300 * 255).astype(np.uint8)
Image.fromarray(normalized, mode='L').save('sdf_combination.png')
