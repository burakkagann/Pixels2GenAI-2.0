import numpy as np
from PIL import Image

CANVAS_SIZE = 512
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

def add_cluster(canvas, cx, cy, num_stars, spread):
    """Drop num_stars stars centred at (cx, cy) with the given Gaussian spread."""
    # TODO 1: draw Gaussian samples for x and y
    # TODO 2: clip to canvas bounds and cast to int
    # TODO 3: assign brightness 255 at the (y, x) coordinates
    pass

# TODO 4: call add_cluster at least three times with different centres,
#         counts (50–300), and spreads (20–100). End with a very wide cluster
#         centred near the middle to act as background stars.

Image.fromarray(canvas, mode='L').save('multi_cluster.png')
