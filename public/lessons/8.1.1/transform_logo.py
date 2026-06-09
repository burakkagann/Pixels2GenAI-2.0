"""
transform_logo.py — twelve image transformations applied to the Python
logo, illustrated side by side. Each transformation is a single-frame
operator: take an image, return a new image. In Module 08 every animation
is built by *time-varying the parameters of these operators*, so the
operators themselves are the building blocks.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


a = np.array(Image.open('python_logo.png').convert('RGB'))
H, W, _ = a.shape


def save(name, arr):
    Image.fromarray(arr.astype(np.uint8)).save(name)


# 1. Dim — multiply intensity by 1/2
save('dim.png', a // 2)

# 2. Horizontal flip — reverse the column axis
save('flip.png', a[:, ::-1])

# 3. Drop the green channel — leaves a purple/magenta logo
g = a.copy()
g[:, :, 1] = 0
save('purple.png', g)

# 4. Channel roll — shift R, G, B by different amounts across the canvas
roll = a.copy()
roll[:, :, 2] = np.roll(roll[:, :, 2], 25, axis=1)
roll[:, :, 1] = np.roll(roll[:, :, 1], 50, axis=0)
save('roll.png', roll)

# 5. Noise overlay — multiply each pixel by random 0..9, divide by 10
rng = np.random.default_rng(0)
noise = rng.integers(0, 10, a.shape)
save('rand.png', (a.astype(np.int64) * noise // 10).clip(0, 255))

# 6. Spaced — only modify every 3rd row/column
spaced = a.astype(np.int64).copy()
spaced[::3, ::3] = (spaced[::3, ::3] * noise[::3, ::3]) // 10
save('spaced.png', spaced.clip(0, 255))

# 7. Quadrant masking — three different colour fills in three quadrants
s = a.copy()
half_h, half_w = H // 2, W // 2
s[half_h:, half_w:, 0] = 0       # bottom-right kills red
s[:half_h, :half_w, 1] = 0       # top-left kills green
s[:half_h, half_w:, 2] = 0       # top-right kills blue
save('square.png', s)

# 8. Mathematical circle — squared distance to the centre
yy, xx = np.mgrid[:H, :W]
cy, cx = H // 2, W // 2
circle = (xx - cx) ** 2 + (yy - cy) ** 2
save('circle.png', (circle // 100).clip(0, 255))

# 9. Logo multiplied by circle — radial brightness mask
gc = a.astype(np.int64).copy()
for ch in range(3):
    gc[:, :, ch] = gc[:, :, ch] * circle
save('logocircle.png', (gc // 20000).clip(0, 255))

# 10. Donut mask — keep pixels in a ring around the centre
donut = np.logical_and(circle < 4500, circle > 3500)
mask = 1 - donut.astype(np.int64)
save('mask.png', (mask * 255).astype(np.uint8))

g_donut = a.astype(np.int64).copy()
for ch in range(3):
    g_donut[:, :, ch] = g_donut[:, :, ch] * mask
save('masked.png', g_donut.clip(0, 255))

print("Saved 10 transformation outputs")
