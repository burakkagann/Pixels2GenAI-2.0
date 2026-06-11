"""
vortex.py - Particle vortex: a swirling spiral of tangential motion around
a central attractor. Each particle is pulled inward (radial force) AND
rotated around the centre (tangential force). The balance between the two
sets the shape of the spiral.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 400, 400
NUM_PARTICLES = 1500
NUM_FRAMES = 120
FPS = 24

CENTRE = np.array([WIDTH / 2, HEIGHT / 2])
INWARD_PULL = 0.06        # radial attraction strength
TANGENTIAL_FORCE = 1.7    # rotational push strength
SPEED_LIMIT = 6.0
DRAG = 0.985

BG = (12, 14, 22)
PARTICLE_COLOUR = (220, 180, 90)
TRAIL_FADE = 0.82         # 0 = no trail, 1 = persistent trail
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
    offsets = positions - CENTRE                              # vectors from centre
    distances = np.linalg.norm(offsets, axis=1, keepdims=True) + 1e-3
    unit_radial = offsets / distances                         # outward unit vectors

    # Tangential = 90-degree rotation of radial
    unit_tangential = np.column_stack([-unit_radial[:, 1], unit_radial[:, 0]])

    radial_force = -INWARD_PULL * offsets                     # pull toward centre
    tangential_force = TANGENTIAL_FORCE * unit_tangential / np.sqrt(distances)

    velocities = (velocities + radial_force + tangential_force) * DRAG
    speeds = np.linalg.norm(velocities, axis=1, keepdims=True)
    over = (speeds > SPEED_LIMIT).flatten()
    velocities[over] *= (SPEED_LIMIT / speeds[over])

    positions = positions + velocities

    # Respawn particles that fell into the centre
    too_close = distances.flatten() < 6
    if too_close.any():
        angles = np.random.uniform(0, 2 * np.pi, too_close.sum())
        radii = np.random.uniform(150, 190, too_close.sum())
        positions[too_close] = CENTRE + np.column_stack(
            [radii * np.cos(angles), radii * np.sin(angles)]
        )
        velocities[too_close] = 0
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
    for frame in range(NUM_FRAMES):
        positions, velocities = step(positions, velocities)
        canvas = render_frame(positions, canvas)
        frames.append(canvas.copy())
        if frame == NUM_FRAMES // 2:
            Image.fromarray(canvas).save('vortex_frame.png')

    imageio.mimsave('vortex.gif', frames, fps=FPS)
    Image.fromarray(canvas).save('vortex_final.png')
    print(f'Wrote vortex.gif ({NUM_FRAMES} frames, {FPS} fps)')


if __name__ == '__main__':
    main()
