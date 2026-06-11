"""
fish_schooling.py - Fish schooling = boids + zone-of-influence model.
Couzin et al. (2002) refined Reynolds's three rules into three concentric
zones around each agent: zone of repulsion (nearest), zone of orientation
(middle), zone of attraction (outer). A fish responds to only one zone at
a time, picked by the closest occupied zone.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 480
NUM_FISH = 90
NUM_FRAMES = 220
FPS = 28

ZONE_REPULSION = 12.0    # tight bubble of personal space
ZONE_ORIENT    = 32.0    # alignment range
ZONE_ATTRACT   = 70.0    # cohesion range

MAX_SPEED = 3.2
TURN_RATE = 0.15         # how quickly fish change heading

BG = (8, 24, 48)
WATER_TINT = (16, 56, 96)
FISH_COLOUR = (200, 230, 240)
# ----------------------------


def normalize(v, eps=1e-6):
    norm = np.linalg.norm(v, axis=-1, keepdims=True) + eps
    return v / norm


def step(positions, velocities):
    n = len(positions)
    deltas = positions[:, None, :] - positions[None, :, :]   # (n,n,2)
    dists = np.linalg.norm(deltas, axis=-1)
    np.fill_diagonal(dists, np.inf)

    desired = velocities.copy()

    for i in range(n):
        rep_mask = dists[i] < ZONE_REPULSION
        if rep_mask.any():
            # only consider repulsion zone
            away = -deltas[i, rep_mask]    # from neighbour to me
            desired[i] = normalize(away.sum(axis=0)) * MAX_SPEED
            continue

        orient_mask = (dists[i] >= ZONE_REPULSION) & (dists[i] < ZONE_ORIENT)
        attract_mask = (dists[i] >= ZONE_ORIENT) & (dists[i] < ZONE_ATTRACT)

        align_dir = np.zeros(2)
        attract_dir = np.zeros(2)
        if orient_mask.any():
            align_dir = velocities[orient_mask].sum(axis=0)
        if attract_mask.any():
            centre = positions[attract_mask].mean(axis=0)
            attract_dir = centre - positions[i]

        steer = align_dir + 0.7 * attract_dir
        if np.linalg.norm(steer) > 1e-3:
            desired[i] = normalize(steer.reshape(1, 2))[0] * MAX_SPEED

    # smoothly turn toward desired velocity
    velocities = velocities + TURN_RATE * (desired - velocities)
    speeds = np.linalg.norm(velocities, axis=-1, keepdims=True)
    over = (speeds > MAX_SPEED).flatten()
    velocities[over] *= (MAX_SPEED / speeds[over])

    positions = positions + velocities
    positions %= np.array([WIDTH, HEIGHT])     # wrap edges
    return positions, velocities


def render(positions, velocities, frame_idx):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    # subtle water gradient
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = tuple(int(BG[i] * (1 - t * 0.4) + WATER_TINT[i] * t * 0.4)
                  for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=c)

    for (x, y), (vx, vy) in zip(positions, velocities):
        heading = np.arctan2(vy, vx)
        tail_x = x - 6 * np.cos(heading)
        tail_y = y - 6 * np.sin(heading)
        draw.line([(tail_x, tail_y), (x, y)], fill=FISH_COLOUR, width=2)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=FISH_COLOUR)
    return np.array(img)


def main():
    np.random.seed(3)
    positions = np.random.rand(NUM_FISH, 2) * np.array([WIDTH, HEIGHT])
    angles = np.random.uniform(0, 2 * np.pi, NUM_FISH)
    velocities = np.column_stack([np.cos(angles), np.sin(angles)]) * MAX_SPEED

    frames = []
    for frame in range(NUM_FRAMES):
        positions, velocities = step(positions, velocities)
        img = render(positions, velocities, frame)
        frames.append(img)
        if frame == NUM_FRAMES // 2:
            Image.fromarray(img).save('fish_frame.png')

    imageio.mimsave('fish_schooling.gif', frames, fps=FPS)
    print(f'Wrote fish_schooling.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
