"""
dla_seeds.py — DLA growth from different seed configurations: a single seed,
a horizontal short line, and three small seed dots. Each panel runs the same
aggregation rule, so the comparison is exclusively about how the *initial*
seed geometry shapes the resulting macro-cluster.

Panel sizes and particle counts are kept moderate so the script finishes in
a few seconds on a typical laptop.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 300
N_PARTICLES = 1500


def run_dla_from_seed(seed_pixels, n_particles, size, rng_seed):
    rng = np.random.default_rng(rng_seed)
    cluster = np.zeros((size, size), dtype=np.int32)
    for sy, sx in seed_pixels:
        cluster[sy, sx] = 1

    seed_arr = np.array(seed_pixels)
    cy = int(seed_arr[:, 0].mean())
    cx = int(seed_arr[:, 1].mean())
    # Initial extent: distance from centroid to the furthest seed.
    max_r = max(5, int(np.max(np.sqrt((seed_arr[:, 0] - cy) ** 2
                                      + (seed_arr[:, 1] - cx) ** 2))))

    for k in range(2, n_particles + 1):
        launch_r = max_r + 8
        kill_r = launch_r + 20

        angle = rng.uniform(0, 2 * np.pi)
        x = int(cx + launch_r * np.cos(angle))
        y = int(cy + launch_r * np.sin(angle))

        while True:
            step = rng.integers(0, 4)
            x += (1, -1, 0, 0)[step]
            y += (0, 0, 1, -1)[step]

            dx = x - cx
            dy = y - cy
            r2 = dx * dx + dy * dy
            if r2 > kill_r * kill_r or x < 1 or x >= size - 1 or y < 1 or y >= size - 1:
                angle = rng.uniform(0, 2 * np.pi)
                x = int(cx + launch_r * np.cos(angle))
                y = int(cy + launch_r * np.sin(angle))
                continue

            if (cluster[y - 1, x] or cluster[y + 1, x]
                    or cluster[y, x - 1] or cluster[y, x + 1]):
                cluster[y, x] = k
                r = int(r2 ** 0.5)
                if r > max_r:
                    max_r = r
                break

    return cluster


def colour_panel(cluster, size, channels):
    """Map a cluster to RGB using attachment order on the given channel triple."""
    panel = np.zeros((size, size, 3), dtype=np.uint8)
    mask = cluster > 0
    if not mask.any():
        return panel
    norm = (cluster[mask].astype(np.float64) - 1) / max(cluster.max() - 1, 1)
    for ch, (base, peak) in enumerate(channels):
        panel[mask, ch] = (base + (peak - base) * norm).astype(np.uint8)
    return panel


configs = [
    ('single', [(SIZE // 2, SIZE // 2)],
     [(50, 200), (160, 220), (200, 60)]),
    ('two',    [(SIZE // 2, SIZE // 3), (SIZE // 2, 2 * SIZE // 3)],
     [(60, 240), (140, 60), (210, 90)]),
    ('triangle', [(SIZE // 4, SIZE // 2),
                  (3 * SIZE // 4, SIZE // 4),
                  (3 * SIZE // 4, 3 * SIZE // 4)],
     [(70, 90),  (200, 230), (90, 240)]),
]

panels = []
for i, (name, seeds, channels) in enumerate(configs):
    print(f'Running DLA with "{name}" seed ({len(seeds)} initial pixels)')
    cluster = run_dla_from_seed(seeds, N_PARTICLES, SIZE, rng_seed=10 + i)
    panels.append(colour_panel(cluster, SIZE, channels))

grid = np.concatenate(panels, axis=1)
Image.fromarray(grid, mode='RGB').save('dla_seeds.png')
print(f"Saved dla_seeds.png — configs: {[c[0] for c in configs]}")
