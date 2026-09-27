import numpy as np
from PIL import Image, ImageDraw

CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
K = 5
AMPLITUDE = 180

PETAL_COLORS = [
    (255, 100, 100),
    (255, 200, 100),
    (255, 255, 100),
    (100, 255, 100),
    (100, 100, 255),
]

def petal_color(theta_value, k):
    # TODO 1: return a colour from PETAL_COLORS based on the angle.
    # The petal index for cos(k·θ) is roughly int(θ · k / π) % len(PETAL_COLORS).
    return PETAL_COLORS[0]

image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), (15, 15, 25))
draw = ImageDraw.Draw(image)

theta = np.linspace(0, 2 * np.pi, 1000)
r = AMPLITUDE * np.cos(K * theta)
x = (CENTER + r * np.cos(theta)).astype(int)
y = (CENTER + r * np.sin(theta)).astype(int)

# TODO 2: draw line segments between consecutive points; use petal_color
# at theta[i] (or the midpoint of theta[i-1] and theta[i]) for each.

image.save('colored_rose.png')
