"""
nbody.py - N-body gravitational simulation. Every body attracts every other
with Newton's inverse-square law. We use leapfrog (velocity Verlet) integration,
which conserves energy much better than Euler for orbital systems.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 540, 540
NUM_FRAMES = 240
FPS = 30

G = 1.6           # gravitational constant (tuned for visual scale)
SOFTENING = 6.0   # close-range cutoff to avoid singularities
DT = 0.45         # leapfrog time step

BG = (4, 6, 18)
TRAIL_FADE = 0.92
PALETTE = [
    (255, 240, 200),    # sun-like
    (140, 200, 255),    # blue planet
    (255, 160, 100),    # mars-ish
    (180, 220, 180),    # green moon
    (220, 180, 255),    # lavender
]
# ----------------------------


def initial_state():
    """A central heavy body plus four orbiting smaller bodies."""
    centre = np.array([WIDTH / 2, HEIGHT / 2])
    masses = [220.0, 5.0, 4.0, 3.0, 2.0]
    radii = [0, 110, 170, 90, 220]
    speeds = [0.0, 1.85, 1.55, 2.10, 1.30]

    positions = [centre]
    velocities = [np.zeros(2)]
    for r, s, angle_deg in zip(radii[1:], speeds[1:], [20, 110, 200, 290]):
        theta = np.deg2rad(angle_deg)
        positions.append(centre + r * np.array([np.cos(theta), np.sin(theta)]))
        # Tangential velocity (perpendicular to radial)
        velocities.append(s * np.array([-np.sin(theta), np.cos(theta)]))

    return np.array(positions, dtype=float), np.array(velocities, dtype=float), \
        np.array(masses, dtype=float)


def accelerations(positions, masses):
    n = len(positions)
    deltas = positions[None, :, :] - positions[:, None, :]            # (n,n,2)
    r2 = (deltas ** 2).sum(axis=-1) + SOFTENING ** 2                  # (n,n)
    inv_r3 = r2 ** -1.5
    np.fill_diagonal(inv_r3, 0.0)
    a = G * (deltas * inv_r3[..., None] * masses[None, :, None]).sum(axis=1)
    return a


def render(canvas, positions, masses):
    canvas = (canvas.astype(np.float32) * TRAIL_FADE).astype(np.uint8)
    canvas[:, :] = np.maximum(canvas, np.array(BG, dtype=np.uint8))
    img = Image.fromarray(canvas)
    draw = ImageDraw.Draw(img)
    for i, ((x, y), m) in enumerate(zip(positions, masses)):
        r = max(2.0, np.sqrt(m) * 0.9)
        c = PALETTE[i % len(PALETTE)]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return np.array(img)


def main():
    positions, velocities, masses = initial_state()
    canvas = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)
    a = accelerations(positions, masses)

    frames = []
    for frame in range(NUM_FRAMES):
        # leapfrog (velocity Verlet)
        velocities += 0.5 * a * DT
        positions += velocities * DT
        a = accelerations(positions, masses)
        velocities += 0.5 * a * DT

        canvas = render(canvas, positions, masses)
        frames.append(canvas.copy())
        if frame == NUM_FRAMES // 2:
            Image.fromarray(canvas).save('nbody_frame.png')

    imageio.mimsave('nbody.gif', frames, fps=FPS)
    Image.fromarray(canvas).save('nbody_final.png')
    print(f'Wrote nbody.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
