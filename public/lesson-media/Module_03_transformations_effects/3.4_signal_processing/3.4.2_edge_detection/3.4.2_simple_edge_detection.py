import numpy as np
from PIL import Image

H, W = 256, 256
image = np.zeros((H, W), dtype=np.float64)
image[80:180, 60:120] = 255                          # rectangle

y, x = np.ogrid[:H, :W]
image[(x - 180) ** 2 + (y - 128) ** 2 <= 40 ** 2] = 255   # circle

# The two Sobel kernels
Gx = np.array([[-1, 0, 1],
               [-2, 0, 2],
               [-1, 0, 1]], dtype=np.float64)
Gy = np.array([[-1, -2, -1],
               [ 0,  0,  0],
               [ 1,  2,  1]], dtype=np.float64)

mag = np.zeros((H, W), dtype=np.float64)
for y_i in range(1, H - 1):
    for x_i in range(1, W - 1):
        n = image[y_i - 1:y_i + 2, x_i - 1:x_i + 2]
        gx = np.sum(Gx * n)
        gy = np.sum(Gy * n)
        mag[y_i, x_i] = np.hypot(gx, gy)             # √(gx² + gy²)

mag = (255 * mag / mag.max()).astype(np.uint8)
Image.fromarray(mag, 'L').save('edge_detection_output.png')
