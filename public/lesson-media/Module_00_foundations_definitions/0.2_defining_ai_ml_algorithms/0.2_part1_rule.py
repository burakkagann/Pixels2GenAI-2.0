"""
A gradient written as an algorithm: a list of exact steps with nothing left to guess.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

WIDTH, HEIGHT = 256, 128

# Step 1: start with a black canvas of the right size.
canvas = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)

# Step 2: visit every pixel. Step 3: make it brighter the further right it sits.
for y in range(HEIGHT):
    for x in range(WIDTH):
        canvas[y, x] = 255 * x / (WIDTH - 1)

# Step 4: save the result. The same steps always give the same picture.
Image.fromarray(canvas).save("gradient.png")
print("Saved gradient.png")
