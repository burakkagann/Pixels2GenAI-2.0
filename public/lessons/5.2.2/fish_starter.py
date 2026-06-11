"""
fish_starter.py - Exercise 3 scaffold for the zonal fish-schooling model.

The simulation loop and rendering are wired up. You implement the zone
selection logic inside `step()`.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 480, 480
NUM_FISH = 80
NUM_FRAMES = 180
FPS = 28
ZONE_REPULSION = 12.0
ZONE_ORIENT = 32.0
ZONE_ATTRACT = 70.0
MAX_SPEED = 3.2
TURN_RATE = 0.15
BG = (8, 24, 48)
FISH_COLOUR = (200, 230, 240)


def normalize(v, eps=1e-6):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + eps)


def step(positions, velocities):
    n = len(positions)
    deltas = positions[:, None, :] - positions[None, :, :]
    dists = np.linalg.norm(deltas, axis=-1)
    np.fill_diagonal(dists, np.inf)

    desired = velocities.copy()
    for i in range(n):
        # TODO 1: build a boolean mask `rep_mask` for neighbours inside
        # ZONE_REPULSION. If any exist, set desired[i] to point AWAY from
        # the sum of those neighbours and continue to next fish.

        # TODO 2: build masks for the orient and attract zones. Use the
        # mean velocity of orient-zone neighbours as align_dir, and
        # (mean_position - my_position) of attract-zone neighbours as
        # attract_dir. desired[i] is normalize(align_dir + 0.7 * attract_dir).
        pass

    velocities = velocities + TURN_RATE * (desired - velocities)
    speeds = np.linalg.norm(velocities, axis=-1, keepdims=True)
    over = (speeds > MAX_SPEED).flatten()
    velocities[over] *= (MAX_SPEED / speeds[over])
    positions = positions + velocities
    positions %= np.array([WIDTH, HEIGHT])
    return positions, velocities


def render(positions, velocities):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    for (x, y), (vx, vy) in zip(positions, velocities):
        heading = np.arctan2(vy, vx)
        tail_x = x - 6 * np.cos(heading)
        tail_y = y - 6 * np.sin(heading)
        draw.line([(tail_x, tail_y), (x, y)], fill=FISH_COLOUR, width=2)
    return np.array(img)


def main():
    np.random.seed(3)
    positions = np.random.rand(NUM_FISH, 2) * np.array([WIDTH, HEIGHT])
    angles = np.random.uniform(0, 2 * np.pi, NUM_FISH)
    velocities = np.column_stack([np.cos(angles), np.sin(angles)]) * MAX_SPEED
    frames = []
    for _ in range(NUM_FRAMES):
        positions, velocities = step(positions, velocities)
        frames.append(render(positions, velocities))
    imageio.mimsave('fish_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
