import numpy as np
from PIL import Image

H, W = 256, 256
image = np.zeros((H, W), dtype=np.float64)
image[50:70,  80:180]  = 255
image[60:180, 115:145] = 255
image[200:230, 200:230] = 200

Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

mag = np.zeros((H, W), dtype=np.float64)
for y in range(1, H - 1):
    for x in range(1, W - 1):
        n = image[y - 1:y + 2, x - 1:x + 2]
        mag[y, x] = np.hypot(np.sum(Gx * n), np.sum(Gy * n))

mag = (255 * mag / mag.max()).astype(np.uint8)
Image.fromarray(mag, 'L').save('my_edges.png')
