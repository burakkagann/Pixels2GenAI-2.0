import numpy as np
from PIL import Image

def mandelbrot_frame(width, height, x_min, x_max, y_min, y_max, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    iterations = np.zeros(C.shape)
    for i in range(max_iter):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask] ** 2 + C[mask]
        iterations[mask] = i
    return iterations

cx, cy = -0.7436, 0.1318
frames = []
for f in range(60):
    progress = f / 59
    width = 3.0 * (500 ** (-progress))
    img = mandelbrot_frame(200, 200,
                            cx - width / 2, cx + width / 2,
                            cy - width / 2, cy + width / 2,
                            150)
    rgb = np.stack([img / 150 * 255,
                    (img / 150 * 128).astype(np.uint8),
                    (255 - img / 150 * 200).astype(np.uint8)], axis=-1)
    rgb[img == 149] = 0   # still bounded after every iteration: inside the set, black
    frames.append(Image.fromarray(rgb.astype(np.uint8)))

frames[0].save('zoom.gif', save_all=True, append_images=frames[1:], duration=33, loop=0)
