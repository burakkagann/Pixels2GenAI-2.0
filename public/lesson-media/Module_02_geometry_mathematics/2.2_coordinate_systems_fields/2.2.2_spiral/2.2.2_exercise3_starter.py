import numpy as np
from PIL import Image

# ... draw_line and canvas setup as before ...

start_color = np.array([255, 50, 50])    # red
end_color   = np.array([50, 50, 255])    # blue

def spiral_with_progress(start_radius, growth_rate, num_points):
    for i in range(num_points):
        # TODO 1: compute theta, r, and (x, y)
        # TODO 2: compute progress = i / (num_points - 1)
        # TODO 3: yield (x, y, progress)
        pass

def interpolate_color(c0, c1, t):
    # TODO 4: clamp t to [0, 1] and return (1-t)*c0 + t*c1 as uint8
    pass

# TODO 5: walk the generator; for each segment, compute its colour with
# interpolate_color(progress) and pass it to draw_line.

Image.fromarray(canvas, mode='RGB').save('color_spiral.png')
