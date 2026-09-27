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

start_color = np.array([255, 50, 50])
end_color   = np.array([50, 50, 255])

def spiral_with_progress(start_radius, growth_rate, num_points):
    for i in range(num_points):
        theta = i * 0.1
        r = start_radius + growth_rate * theta
        x = int(cx + r * np.cos(theta))
        y = int(cy + r * np.sin(theta))
        progress = i / (num_points - 1) if num_points > 1 else 0
        yield x, y, progress

def interpolate_color(c0, c1, t):
    t = max(0.0, min(1.0, t))
    return ((1 - t) * c0 + t * c1).astype(np.uint8)

points = spiral_with_progress(5, 0.5, 500)
prev_x, prev_y, _ = next(points)
for x, y, progress in points:
    color = interpolate_color(start_color, end_color, progress)
    draw_line(canvas, prev_x, prev_y, x, y, color)
    prev_x, prev_y = x, y

Image.fromarray(canvas, mode='RGB').save('color_spiral.png')
