# A sunburst: 24 lines from a centre point to evenly-spaced angles
import numpy as np
from PIL import Image

canvas = np.zeros((400, 400), dtype=np.uint8)
cx, cy, radius = 200, 200, 180

angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
for theta in angles:
    ex = int(cx + radius * np.cos(theta))
    ey = int(cy + radius * np.sin(theta))
    n = max(abs(ex - cx), abs(ey - cy)) + 1
    xs = np.linspace(cx, ex, n).round().astype(int)
    ys = np.linspace(cy, ey, n).round().astype(int)
    canvas[ys, xs] = 255

Image.fromarray(canvas).save('sunburst.png')
