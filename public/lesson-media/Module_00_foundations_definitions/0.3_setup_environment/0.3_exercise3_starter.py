"""
Stripes: a first picture of your own, on your own computer. Fill in the TODOs.

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
    # TODO 1: Work out which stripe this column belongs to.
    # Why: columns 0 to 39 are stripe 0, columns 40 to 79 are stripe 1, and so on.
    # Whole-number division does this: x // STRIPE_WIDTH.
    stripe_number = 0

    # TODO 2: Use COLOUR_ONE for even stripes and COLOUR_TWO for odd ones.
    # Why: alternating is what makes them stripes. stripe_number % 2 is 0 when even.
    colour = COLOUR_ONE

    # TODO 3: Paint the whole column.
    # Why: canvas[:, x] means "every row, in column x". Assign colour to it.
    pass

Image.fromarray(canvas).save("my_stripes.png")
print("Saved my_stripes.png")
