import random
import numpy as np
from PIL import Image
import imageio.v2 as imageio

particles = []
for _ in range(500):
    particles.append({
        'x': 150 + random.randint(0, 100),
        'y': 100 + random.randint(0, 100),
        'vx': random.uniform(-1, 2),
        'vy': random.uniform(-0.5, 0.5),
        'delay': random.randint(0, 60),
    })

frames = []
for frame in range(80):
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    for p in particles:
        if p['delay'] > 0:
            p['delay'] -= 1
            colour = (50, 40, 30)
        else:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 1.05
            colour = (194, 178, 128)
        x, y = int(p['x']), int(p['y'])
        if 0 <= x < 297 and 0 <= y < 197:
            img[y:y + 3, x:x + 3] = colour
    frames.append(img)

imageio.mimsave('quick_sand.gif', frames, fps=24)
