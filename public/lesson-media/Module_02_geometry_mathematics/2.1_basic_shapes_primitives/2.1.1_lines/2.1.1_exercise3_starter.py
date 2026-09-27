import numpy as np
from PIL import Image

def draw_line(canvas, x0, y0, x1, y1):
    # TODO 1: copy the linspace-based line drawing into this function
    pass

canvas = np.zeros((400, 400), dtype=np.uint8)
cx, cy = 200, 200
radius = 180
num_rays = 24

# TODO 2: generate num_rays evenly-spaced angles from 0 to 2*pi
# angles = ...

# TODO 3: for each angle, compute the endpoint (ex, ey) and call draw_line
# for theta in angles:
#     ex = ...
#     ey = ...
#     draw_line(canvas, cx, cy, ex, ey)

Image.fromarray(canvas).save('sunburst.png')
