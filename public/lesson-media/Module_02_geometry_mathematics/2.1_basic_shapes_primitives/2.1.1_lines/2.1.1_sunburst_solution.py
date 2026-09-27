import numpy as np
from PIL import Image

def draw_line(canvas, x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    canvas[ys, xs] = 255

canvas = np.zeros((400, 400), dtype=np.uint8)
cx, cy = 200, 200
radius = 180
num_rays = 24

angles = np.linspace(0, 2 * np.pi, num_rays, endpoint=False)
for theta in angles:
    ex = int(cx + radius * np.cos(theta))
    ey = int(cy + radius * np.sin(theta))
    draw_line(canvas, cx, cy, ex, ey)

Image.fromarray(canvas).save('sunburst.png')
