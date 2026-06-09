"""
simple_julia.py — render a Julia set for the classic parameter c = -0.7 + 0.27015j
using the escape-time iteration z = z^2 + c. The Mandelbrot iteration runs the
same map but with z_0 = 0 and c varying; the Julia iteration fixes c and varies
z_0 instead, so every pixel becomes the starting point of its own orbit.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 600
MAX_ITER = 200
C = complex(-0.7, 0.27015)  # one of the classic dendrite-like Julia parameters

# Build a complex grid centred at zero. The Julia set lives inside the disc
# of radius ~2 in the complex plane, so a symmetric viewport works well.
x = np.linspace(-1.6, 1.6, SIZE)
y = np.linspace(-1.6, 1.6, SIZE)
real, imag = np.meshgrid(x, y)
z = real + 1j * imag  # every pixel is its own starting z_0

# Escape-time iteration. Identical to Mandelbrot, but c is a scalar that
# applies to every grid point (broadcasts over the whole array).
iterations = np.zeros(z.shape, dtype=np.int32)
for _ in range(MAX_ITER):
    bounded = np.abs(z) <= 2
    z[bounded] = z[bounded] ** 2 + C
    iterations[bounded] += 1

# Grayscale render. Inside-set pixels (iterations == MAX_ITER) stay black;
# the fringe brightens with the escape count.
gray = np.zeros((SIZE, SIZE), dtype=np.uint8)
outside = iterations < MAX_ITER
gray[outside] = (iterations[outside] / MAX_ITER * 255).astype(np.uint8)

Image.fromarray(gray, mode='L').save('simple_julia.png')
print(f"Saved simple_julia.png — c = {C}, {SIZE}x{SIZE}, max_iter = {MAX_ITER}")
