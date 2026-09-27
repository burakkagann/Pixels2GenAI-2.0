import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2

# Two pendulums — X and Y
FREQ_X, AMP_X, PHASE_X = 3, 200, 0
FREQ_Y, AMP_Y, PHASE_Y = 2, 200, np.pi / 2

DAMPING = 0.002

t = np.linspace(0, 100, 5000)
decay = np.exp(-DAMPING * t)

x = CENTER + AMP_X * np.sin(FREQ_X * t + PHASE_X) * decay
y = CENTER + AMP_Y * np.sin(FREQ_Y * t + PHASE_Y) * decay

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (10, 10, 20))
draw = ImageDraw.Draw(image)
points = list(zip(x.astype(int), y.astype(int)))
draw.line(points, fill=(100, 200, 255), width=1)
image.save('simple_harmonograph.png')
