import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

positions = np.random.rand(30, 2) * 400
velocities = (np.random.rand(30, 2) - 0.5) * 4

frames = []
for _ in range(150):
    img = Image.new('RGB', (400, 400), (20, 20, 30))
    draw = ImageDraw.Draw(img)
    for x, y in positions:
        draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(0, 200, 200))
    frames.append(np.array(img))

    centre = positions.mean(axis=0)
    positions += (centre - positions) * 0.01 + velocities * 0.5
    positions %= 400  # wrap at edges

imageio.mimsave('simple_flock.gif', frames, fps=20)
