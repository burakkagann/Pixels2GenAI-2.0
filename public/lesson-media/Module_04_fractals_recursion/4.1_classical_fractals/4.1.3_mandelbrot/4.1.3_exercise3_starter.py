import numpy as np
from PIL import Image

def mandelbrot_zoom(center_x, center_y, zoom_level, size=512, max_iter=200):
    """Generate a Mandelbrot image at the specified location and zoom."""
    # TODO 1: compute x_min, x_max, y_min, y_max from centre + zoom
    #         baseline viewport is roughly 3.5 wide and 3.0 tall

    # TODO 2: build the complex grid (np.linspace + meshgrid + 1j)

    # TODO 3: run the escape-time iteration loop

    # TODO 4: map iterations to colour and return an RGB array
    pass

if __name__ == '__main__':
    img = mandelbrot_zoom(-0.745, 0.113, zoom_level=50, max_iter=300)
    Image.fromarray(img).save('my_zoom.png')
