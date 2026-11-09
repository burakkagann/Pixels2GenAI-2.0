"""
Stripes: a first picture of your own, on your own computer.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

# ========== CONFIG: experiment after the TODOs are done ==========
STRIPE_WIDTH = 40               # Pixels across each stripe
COLOUR_ONE = (61, 85, 136)      # Red, green, blue, each from 0 to 255
COLOUR_TWO = (243, 239, 231)
# =================================================================

WIDTH, HEIGHT = 800, 400

# A black canvas: HEIGHT rows, WIDTH columns, three colour numbers per pixel.
canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

for x in range(WIDTH):
    stripe_number = x // STRIPE_WIDTH

    if stripe_number % 2 == 0:
        colour = COLOUR_ONE
    else:
        colour = COLOUR_TWO

    canvas[:, x] = colour

Image.fromarray(canvas).save("my_stripes.png")
print("Saved my_stripes.png")
