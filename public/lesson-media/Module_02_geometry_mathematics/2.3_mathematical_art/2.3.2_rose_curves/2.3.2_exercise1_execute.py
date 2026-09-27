import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
K_PARAMETER = 5
AMPLITUDE = 180

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (15, 15, 25))
draw = ImageDraw.Draw(image)

theta = np.linspace(0, 2 * np.pi, 1000)
r = AMPLITUDE * np.cos(K_PARAMETER * theta)

x = CENTER + r * np.cos(theta)
y = CENTER + r * np.sin(theta)

points = list(zip(x.astype(int), y.astype(int)))
draw.line(points, fill=(255, 100, 150), width=2)

image.save('simple_rose.png')
