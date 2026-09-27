import numpy as np
from PIL import Image, ImageDraw

canvas = np.zeros((400, 400, 3), dtype=np.uint8) + np.array([30, 30, 40], dtype=np.uint8)

square = np.array(
    [[-50, -50], [50, -50], [50, 50], [-50, 50]],
    dtype=np.float64,
)

# 2×3 affine: scale by 1.5, translate (+200, 0)
affine = np.array([
    [1.5, 0.0, 200.0],
    [0.0, 1.5,   0.0],
])

ones = np.ones((square.shape[0], 1))
homogeneous = np.hstack([square, ones])           # shape (4, 3)
transformed = (affine @ homogeneous.T).T          # shape (4, 2)

# Place both squares on the canvas
left  = (square      + np.array([100, 200])).astype(int)
right = (transformed + np.array([100, 200])).astype(int)

img = Image.fromarray(canvas)
draw = ImageDraw.Draw(img)
draw.polygon([tuple(p) for p in left],  fill=(70, 130, 200))
draw.polygon([tuple(p) for p in right], fill=(230, 150, 50))
img.save('simple_affine.png')
