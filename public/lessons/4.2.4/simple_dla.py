"""
simple_dla.py — diffusion-limited aggregation on a grid. Seed one stuck
pixel at the centre. Repeatedly release a walker on a launch circle around
the cluster. Step the walker by random nearest-neighbour moves until it
either touches the cluster (then stick) or wanders too far (then kill).
The result is a branching, dendritic structure that grows outward.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


SIZE = 600
N_PARTICLES = 4000
SEED = 3


def run_dla(size=SIZE, n_particles=N_PARTICLES, seed=SEED):
    """Return an int32 grid where pixel = particle index when stuck, 0 otherwise."""
    rng = np.random.default_rng(seed)
    cluster = np.zeros((size, size), dtype=np.int32)

    cx, cy = size // 2, size // 2
    cluster[cy, cx] = 1
    max_radius = 5
    kill_radius = max_radius + 30

    for k in range(2, n_particles + 1):
        # Launch on a circle that expands as the cluster grows.
        launch_r = max_radius + 10
        kill_r = launch_r + 30

        angle = rng.uniform(0, 2 * np.pi)
        x = int(cx + launch_r * np.cos(angle))
        y = int(cy + launch_r * np.sin(angle))

        while True:
            # Random nearest-neighbour step.
            step = rng.integers(0, 4)
            x += (1, -1, 0, 0)[step]
            y += (0, 0, 1, -1)[step]

            # Out-of-bounds or beyond kill radius → discard and start a new walker.
            dx = x - cx
            dy = y - cy
            r2 = dx * dx + dy * dy
            if r2 > kill_r * kill_r or x < 1 or x >= size - 1 or y < 1 or y >= size - 1:
                # Re-launch on the launch circle.
                angle = rng.uniform(0, 2 * np.pi)
                x = int(cx + launch_r * np.cos(angle))
                y = int(cy + launch_r * np.sin(angle))
                continue

            # Check stick condition: any 4-neighbour is part of the cluster.
            if (cluster[y - 1, x] or cluster[y + 1, x]
                    or cluster[y, x - 1] or cluster[y, x + 1]):
                cluster[y, x] = k
                r = int(r2 ** 0.5)
                if r > max_radius:
                    max_radius = r
                break

    return cluster


cluster = run_dla()

# Colour by attachment order so the visual reads as time-stamped growth.
order = cluster.astype(np.float64)
order[order > 0] = (order[order > 0] - order[order > 0].min()) / max(
    order[order > 0].max() - order[order > 0].min(), 1.0)

# Phase-shifted sine palette for that classic DLA "branching crystal" look.
rgb = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
mask = cluster > 0
norm = order[mask]
rgb[mask, 0] = (128 + 127 * np.sin(norm * 4 + 0)).astype(np.uint8)
rgb[mask, 1] = (128 + 127 * np.sin(norm * 4 + 2)).astype(np.uint8)
rgb[mask, 2] = (128 + 127 * np.sin(norm * 4 + 4)).astype(np.uint8)

Image.fromarray(rgb, mode='RGB').save('simple_dla.png')
print(f"Saved simple_dla.png — {int(mask.sum())} stuck particles")
