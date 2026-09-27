import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2

START_COLOR = (100, 255, 255)
END_COLOR   = (20, 40, 80)

def faded_color(decay_value):
    r = int(START_COLOR[0] * decay_value + END_COLOR[0] * (1 - decay_value))
    g = int(START_COLOR[1] * decay_value + END_COLOR[1] * (1 - decay_value))
    b = int(START_COLOR[2] * decay_value + END_COLOR[2] * (1 - decay_value))
    return (r, g, b)

t = np.linspace(0, 100, 5000)
decay = np.exp(-0.003 * t)
x = CENTER + 200 * np.sin(5 * t) * decay
y = CENTER + 200 * np.sin(4 * t + np.pi / 2) * decay

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (10, 10, 20))
draw = ImageDraw.Draw(image)

for i in range(1, len(t)):
    color = faded_color(decay[i])
    draw.line([(int(x[i-1]), int(y[i-1])), (int(x[i]), int(y[i]))],
              fill=color, width=1)

image.save('colored_harmonograph.png')
