"""
vortex_starter.py - Exercise 3 scaffold.

The frame loop, rendering, and GIF export are wired up. You implement the
force model: two TODOs inside `step()`.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 400, 400
NUM_PARTICLES = 1200
NUM_FRAMES = 100
FPS = 24

CENTRE = np.array([WIDTH / 2, HEIGHT / 2])
INWARD_PULL = 0.06
TANGENTIAL_FORCE = 1.5
SPEED_LIMIT = 6.0
DRAG = 0.985

BG = (12, 14, 22)
PARTICLE_COLOUR = (220, 180, 90)
TRAIL_FADE = 0.82
# ----------------------------


def spawn_particles(n):
    angles = np.random.uniform(0, 2 * np.pi, n)
    radii = np.random.uniform(140, 190, n)
    positions = CENTRE + np.column_stack(
        [radii * np.cos(angles), radii * np.sin(angles)]
    )
    velocities = np.zeros_like(positions)
    return positions, velocities


def step(positions, velocities):
    offsets = positions - CENTRE
    distances = np.linalg.norm(offsets, axis=1, keepdims=True) + 1e-3
    unit_radial = offsets / distances

    # TODO 1: compute the tangential unit vectors.
    # Hint: rotate unit_radial by 90 degrees. For a 2D vector (x, y),
    #       a 90-degree counter-clockwise rotation is (-y, x).
    unit_tangential = np.zeros_like(unit_radial)

    # TODO 2: compose the radial and tangential force terms.
    # radial_force should pull toward the centre (i.e. point in -offsets direction).
    # tangential_force should rotate around the centre, getting stronger
    # near the centre (try dividing by sqrt(distance)).
    radial_force = np.zeros_like(offsets)
    tangential_force = np.zeros_like(offsets)

    velocities = (velocities + radial_force + tangential_force) * DRAG
    speeds = np.linalg.norm(velocities, axis=1, keepdims=True)
    over = (speeds > SPEED_LIMIT).flatten()
    velocities[over] *= (SPEED_LIMIT / speeds[over])

    positions = positions + velocities
    return positions, velocities


def render_frame(positions, canvas):
    canvas = (canvas.astype(np.float32) * TRAIL_FADE).astype(np.uint8)
    canvas[:, :] = np.maximum(canvas, np.array(BG, dtype=np.uint8) // 6)
    xs = np.clip(positions[:, 0].astype(int), 0, WIDTH - 1)
    ys = np.clip(positions[:, 1].astype(int), 0, HEIGHT - 1)
    canvas[ys, xs] = PARTICLE_COLOUR
    return canvas


def main():
    np.random.seed(7)
    positions, velocities = spawn_particles(NUM_PARTICLES)
    canvas = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)

    frames = []
    for _ in range(NUM_FRAMES):
        positions, velocities = step(positions, velocities)
        canvas = render_frame(positions, canvas)
        frames.append(canvas.copy())

    imageio.mimsave('vortex_starter.gif', frames, fps=FPS)
    print('Wrote vortex_starter.gif')


if __name__ == '__main__':
    main()
