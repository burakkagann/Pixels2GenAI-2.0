"""
colored_julia.py — render the c = -0.7 + 0.27015j Julia set with a phase-shifted
sine-rainbow palette, then optionally save a smaller version. The palette uses
three sine waves at the same frequency but offset by 0, 2, 4 radians for each
channel — a classic phase-offset rainbow that makes escape-time bands visible.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 800
MAX_ITER = 250
C = complex(-0.7, 0.27015)

x = np.linspace(-1.6, 1.6, SIZE)
y = np.linspace(-1.6, 1.6, SIZE)
real, imag = np.meshgrid(x, y)
z = real + 1j * imag

iterations = np.zeros(z.shape, dtype=np.int32)
for _ in range(MAX_ITER):
    bounded = np.abs(z) <= 2
    z[bounded] = z[bounded] ** 2 + C
    iterations[bounded] += 1

# Cyclic rainbow palette. Phase offsets of 0, 2, 4 radians give R, G, B channels
# that sweep through the wheel at different points along the escape ramp.
image = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
norm = iterations / MAX_ITER
outside = iterations < MAX_ITER

freq = 8.0  # how many colour cycles to fit across the escape ramp
image[outside, 0] = (128 + 127 * np.sin(norm[outside] * freq + 0)).astype(np.uint8)
image[outside, 1] = (128 + 127 * np.sin(norm[outside] * freq + 2)).astype(np.uint8)
image[outside, 2] = (128 + 127 * np.sin(norm[outside] * freq + 4)).astype(np.uint8)
# inside set: stays black

Image.fromarray(image, mode='RGB').save('colored_julia.png')
print(f"Saved colored_julia.png — c = {C}, palette frequency = {freq}")
