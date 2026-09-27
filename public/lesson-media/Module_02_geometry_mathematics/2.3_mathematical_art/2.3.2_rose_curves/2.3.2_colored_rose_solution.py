import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
K = 5
AMPLITUDE = 180

PETAL_COLORS = [
    (255, 100, 100), (255, 200, 100), (255, 255, 100),
    (100, 255, 100), (100, 100, 255),
]

def petal_color(theta_value, k):
    petal_index = int(theta_value * k / np.pi) % len(PETAL_COLORS)
    return PETAL_COLORS[petal_index]

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (15, 15, 25))
draw = ImageDraw.Draw(image)

theta = np.linspace(0, 2 * np.pi, 1000)
r = AMPLITUDE * np.cos(K * theta)
x = (CENTER + r * np.cos(theta)).astype(int)
y = (CENTER + r * np.sin(theta)).astype(int)

for i in range(1, len(theta)):
    color = petal_color(theta[i], K)
    draw.line([(x[i - 1], y[i - 1]), (x[i], y[i])], fill=color, width=2)

image.save('colored_rose.png')
