import numpy as np
from PIL import Image

def draw_line(canvas, x0, y0, x1, y1, color):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    h, w = canvas.shape[:2]
    inside = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    canvas[ys[inside], xs[inside]] = color

WIDTH, HEIGHT = 512, 512
cx, cy = WIDTH // 2, HEIGHT // 2
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

def spiral_points(start_radius=10, growth_rate=4.0, num_points=500):
    for i in range(num_points):
        theta = i * 0.1
        r = start_radius + growth_rate * theta
        x = int(cx + r * np.cos(theta))
        y = int(cy + r * np.sin(theta))
        yield x, y

points = spiral_points()
prev_x, prev_y = next(points)
for x, y in points:
    draw_line(canvas, prev_x, prev_y, x, y, [255, 255, 255])
    prev_x, prev_y = x, y

Image.fromarray(canvas, mode='RGB').save('simple_spiral.png')
