import numpy as np
from PIL import Image

N_TILES, N_FRAMES, SCATTER_RADIUS = 16, 60, 350

flower = np.array(Image.open('flower.png').convert('RGB'))
H, W, _ = flower.shape
th, tw = H // N_TILES, W // N_TILES

# Per-tile arrays: home position + scatter offset
home_yx = np.array([(r * th, c * tw) for r in range(N_TILES) for c in range(N_TILES)])
rng = np.random.default_rng(7)
angles = rng.uniform(0, 2 * np.pi, len(home_yx))
radii = rng.uniform(SCATTER_RADIUS * 0.5, SCATTER_RADIUS, len(home_yx))
scatter_dyx = np.stack([(radii * np.sin(angles)).astype(int),
                        (radii * np.cos(angles)).astype(int)], axis=1)

frames = []
for f in range(N_FRAMES):
    t = f / (N_FRAMES - 1)
    progress = 1 - (1 - t) ** 3                       # ease-out cubic
    offsets = (scatter_dyx * (1 - progress)).astype(int)
    canvas = np.full(flower.shape, 12, dtype=np.uint8)
    for (cy, cx), (dy, dx) in zip(home_yx, offsets):
        y, x = cy + dy, cx + dx
        if 0 <= y <= H - th and 0 <= x <= W - tw:
            canvas[y:y+th, x:x+tw] = flower[cy:cy+th, cx:cx+tw]
    frames.append(Image.fromarray(canvas))

frames[0].save('flower_assembly.gif', save_all=True,
               append_images=frames[1:], duration=50, loop=0)
