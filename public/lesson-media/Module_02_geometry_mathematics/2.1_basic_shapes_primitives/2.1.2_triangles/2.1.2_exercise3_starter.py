import numpy as np
from PIL import Image

def draw_filled_triangle(canvas, v1, v2, v3, color):
    """Fill the triangle (v1, v2, v3) with `color` on an RGB canvas."""
    # TODO 1: build x, y coordinate grids with np.meshgrid
    # TODO 2: define an edge() helper and compute the three edge tests
    # TODO 3: combine with & into a mask, then assign color where the mask is True
    pass

def create_gradient_sky(height, width):
    """Vertical gradient from midnight blue (top) to sunset orange (bottom)."""
    sky = np.zeros((height, width, 3), dtype=np.uint8)
    # TODO 4: interpolate per-row between top and bottom colours, write into sky[y, :]
    return sky

height, width = 400, 500
canvas = create_gradient_sky(height, width)

# TODO 5: define at least 3 mountains as dicts with peak/left/right/color,
# then draw them back to front by calling draw_filled_triangle for each.

Image.fromarray(canvas).save('triangle_mountain.png')
