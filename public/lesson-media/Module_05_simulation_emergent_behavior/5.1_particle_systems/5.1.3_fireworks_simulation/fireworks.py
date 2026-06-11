"""
fireworks.py - A two-stage particle effect. Rockets rise from the bottom
edge of the canvas, decelerate at their apex, then explode into a radial
burst of glowing particles that fall under gravity.

Pixels2GenAI Project
"""

import random
import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 480
NUM_FRAMES = 200
FPS = 30

GRAVITY = 0.18
ROCKET_INTERVAL = 22                # frames between launches
BURST_PARTICLES = 90
BURST_SPEED = 4.2
PARTICLE_LIFE = 70                  # frames

BG = (10, 8, 18)
TRAIL_FADE = 0.88
PALETTE = [
    (255, 100, 80),
    (255, 200, 80),
    (120, 200, 255),
    (200, 120, 255),
    (160, 255, 180),
]
# ----------------------------


class Rocket:
    def __init__(self):
        self.x = random.uniform(0.2, 0.8) * WIDTH
        self.y = HEIGHT - 5.0
        self.vy = -random.uniform(8.0, 10.5)
        self.colour = random.choice(PALETTE)
        self.exploded = False

    def step(self):
        self.vy += GRAVITY
        self.y += self.vy
        # Explode at apex (when vy turns positive)
        if self.vy > -0.5 and not self.exploded:
            self.exploded = True


class Spark:
    def __init__(self, x, y, colour):
        angle = random.uniform(0, 2 * np.pi)
        speed = random.uniform(0.5, BURST_SPEED)
        self.x = x
        self.y = y
        self.vx = speed * np.cos(angle)
        self.vy = speed * np.sin(angle)
        self.life = PARTICLE_LIFE
        self.colour = colour

    def step(self):
        self.vy += GRAVITY * 0.5
        self.x += self.vx
        self.y += self.vy
        self.life -= 1


def render(canvas, rockets, sparks):
    canvas = (canvas.astype(np.float32) * TRAIL_FADE).astype(np.uint8)
    canvas[:, :] = np.maximum(canvas, np.array(BG, dtype=np.uint8))

    for r in rockets:
        x, y = int(r.x), int(r.y)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            canvas[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = r.colour

    for s in sparks:
        x, y = int(s.x), int(s.y)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            fade = max(0.0, s.life / PARTICLE_LIFE)
            colour = tuple(int(c * fade) for c in s.colour)
            canvas[y, x] = colour
    return canvas


def main():
    random.seed(11)
    np.random.seed(11)
    rockets = []
    sparks = []
    canvas = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)
    frames = []

    for frame in range(NUM_FRAMES):
        if frame % ROCKET_INTERVAL == 0:
            rockets.append(Rocket())

        new_rockets = []
        for r in rockets:
            r.step()
            if r.exploded:
                for _ in range(BURST_PARTICLES):
                    sparks.append(Spark(r.x, r.y, r.colour))
            else:
                new_rockets.append(r)
        rockets = new_rockets

        for s in sparks:
            s.step()
        sparks = [s for s in sparks if s.life > 0 and s.y < HEIGHT]

        canvas = render(canvas, rockets, sparks)
        frames.append(canvas.copy())

        if frame == 110:
            Image.fromarray(canvas).save('fireworks_frame.png')

    imageio.mimsave('fireworks.gif', frames, fps=FPS)
    print(f'Wrote fireworks.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
