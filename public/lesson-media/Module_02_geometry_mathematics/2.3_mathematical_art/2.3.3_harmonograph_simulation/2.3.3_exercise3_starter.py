import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2

START_COLOR = (100, 255, 255)   # bright cyan (full energy)
END_COLOR   = (20, 40, 80)      # dark blue (decayed)

def faded_color(decay_value):
    # TODO 1: interpolate between START_COLOR (decay = 1) and END_COLOR (decay → 0).
    # Result: tuple of three uint8s.
    pass

t = np.linspace(0, 100, 5000)
decay = np.exp(-0.003 * t)
x = CENTER + 200 * np.sin(5 * t) * decay
y = CENTER + 200 * np.sin(4 * t + np.pi / 2) * decay

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (10, 10, 20))
draw = ImageDraw.Draw(image)

# TODO 2: per-segment loop: for each i, colour = faded_color(decay[i]),
# then draw.line from (x[i-1], y[i-1]) to (x[i], y[i]) with that colour.

image.save('colored_harmonograph.png')
