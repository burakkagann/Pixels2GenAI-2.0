import numpy as np
from PIL import Image

def mandelbrot_zoom(center_x, center_y, zoom_level, size=512, max_iter=200):
    x_range = 3.5 / zoom_level
    y_range = 3.0 / zoom_level
    x_min, x_max = center_x - x_range/2, center_x + x_range/2
    y_min, y_max = center_y - y_range/2, center_y + y_range/2

    real = np.linspace(x_min, x_max, size)
    imag = np.linspace(y_min, y_max, size)
    real_grid, imag_grid = np.meshgrid(real, imag)
    c = real_grid + 1j * imag_grid

    z = np.zeros_like(c)
    iterations = np.zeros(c.shape, dtype=np.int32)
    for _ in range(max_iter):
        bounded = np.abs(z) <= 2
        z[bounded] = z[bounded]**2 + c[bounded]
        iterations[bounded] += 1

    norm = iterations / max_iter
    outside = iterations < max_iter
    image = np.zeros((size, size, 3), dtype=np.uint8)
    image[outside, 0] = (128 + 127*np.sin(norm[outside]*10 + 0)).astype(np.uint8)
    image[outside, 1] = (128 + 127*np.sin(norm[outside]*10 + 2)).astype(np.uint8)
    image[outside, 2] = (128 + 127*np.sin(norm[outside]*10 + 4)).astype(np.uint8)
    return image

if __name__ == '__main__':
    Image.fromarray(mandelbrot_zoom(-0.745, 0.113, 50, max_iter=300)).save('my_zoom.png')
