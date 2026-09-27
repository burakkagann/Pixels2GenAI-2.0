import numpy as np
from PIL import Image

# 1. Grid of complex numbers covering the classic Mandelbrot viewport
x = np.linspace(-2.5, 1.0, 512)
y = np.linspace(-1.5, 1.5, 512)
real, imag = np.meshgrid(x, y)
c = real + 1j * imag

# 2. Iterate z = z^2 + c, tracking how long each point survives
z = np.zeros_like(c)
iterations = np.zeros(c.shape, dtype=np.int32)
for _ in range(100):
    bounded = np.abs(z) <= 2
    z[bounded] = z[bounded]**2 + c[bounded]
    iterations[bounded] += 1

# 3. Map iteration counts to a grayscale image
gray = (iterations / 100 * 255).astype(np.uint8)
gray[iterations == 100] = 0   # never escaped: inside the set, painted black
Image.fromarray(gray).save('mandelbrot_basic.png')
