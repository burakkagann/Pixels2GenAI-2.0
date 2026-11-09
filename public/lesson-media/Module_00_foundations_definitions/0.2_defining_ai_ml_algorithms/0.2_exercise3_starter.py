"""
A nearest-neighbour painter: a learner with no formula at all. Each pixel copies
the colour of the example closest to it. Fill in the TODOs.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

# ========== CONFIG: experiment after the TODOs are done ==========
EXAMPLE_COUNT = 12   # How many coloured examples the painter gets
SEED = 5             # Change it for new example positions and colours
# =================================================================

SIZE = 300
random_numbers = np.random.default_rng(SEED)

# The examples: a position and a colour for each. Think of them as training data.
palette = np.array([[0, 131, 138], [61, 85, 136], [255, 72, 176], [243, 239, 231]])
example_positions = random_numbers.uniform(0, SIZE, (EXAMPLE_COUNT, 2))
example_colours = palette[random_numbers.integers(0, len(palette), EXAMPLE_COUNT)]

image = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

for y in range(SIZE):
    for x in range(SIZE):
        # TODO 1: Measure how far this pixel is from every example.
        # Why: "closest" needs a distance. np.hypot(across, down) gives one for each
        # example when across and down are arrays. Column 0 of example_positions
        # holds the x values and column 1 the y values.
        distances = np.zeros(EXAMPLE_COUNT)

        # TODO 2: Find the position of the smallest distance.
        # Why: that example is this pixel's nearest neighbour. Use np.argmin.
        nearest = 0

        # TODO 3: Give this pixel the nearest example's colour.
        # Why: this copy is the painter's whole "prediction". Assign to image[y, x].
        pass

Image.fromarray(image).save("nearest_painter.png")
print("Saved nearest_painter.png")
