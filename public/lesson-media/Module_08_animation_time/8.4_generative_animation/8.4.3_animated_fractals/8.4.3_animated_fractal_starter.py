import numpy as np
from PIL import Image

def compute_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iter):
    # TODO 1: create the complex grid with meshgrid
    # TODO 2: iterate z = z² + c with boolean masking
    # TODO 3: return the iteration counts
    pass

def iterations_to_colors(iterations, max_iter):
    # TODO 4: convert counts to RGB; inside-set points are black
    pass

def zoom_window(frame, total_frames, cx, cy, init_w, zoom):
    # TODO 5: exponential interpolation of the window width
    pass

def render_animation(cx, cy, zoom, n_frames):
    frames = []
    for f in range(n_frames):
        xmin, xmax, ymin, ymax = zoom_window(f, n_frames, cx, cy, 3.0, zoom)
        iters = compute_mandelbrot(400, 400, xmin, xmax, ymin, ymax, 200)
        rgb = iterations_to_colors(iters, 200)
        frames.append(Image.fromarray(rgb))
    return frames
