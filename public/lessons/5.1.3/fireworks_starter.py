"""
fireworks_starter.py - Exercise 3 scaffold.

The render loop is wired up. You implement Spark.__init__ and Spark.step.

Pixels2GenAI Project
"""

import random
import numpy as np
from PIL import Image
import imageio.v2 as imageio

WIDTH, HEIGHT = 480, 480
NUM_FRAMES = 180
FPS = 30
GRAVITY = 0.18
BURST_PARTICLES = 80
BURST_SPEED = 4.0
PARTICLE_LIFE = 60
BG = (10, 8, 18)
TRAIL_FADE = 0.88


class Rocket:
    def __init__(self):
        self.x = random.uniform(0.2, 0.8) * WIDTH
        self.y = HEIGHT - 5.0
        self.vy = -random.uniform(8.0, 10.0)
        self.colour = (255, 200, 80)
        self.exploded = False

    def step(self):
        self.vy += GRAVITY
        self.y += self.vy
        if self.vy > -0.5 and not self.exploded:
            self.exploded = True


class Spark:
    def __init__(self, x, y, colour):
        # TODO 1: pick a random angle in [0, 2*pi) and a random speed in [0.5, BURST_SPEED]
        # then set self.vx = speed * cos(angle), self.vy = speed * sin(angle)
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.life = PARTICLE_LIFE
        self.colour = colour

    def step(self):
        # TODO 2: apply a half-strength gravity to vy, then advance position,
        # then decrement self.life by 1.
        pass


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
            canvas[y, x] = tuple(int(c * fade) for c in s.colour)
    return canvas


def main():
    random.seed(11)
    np.random.seed(11)
    rockets, sparks, frames = [], [], []
    canvas = np.full((HEIGHT, WIDTH, 3), BG, dtype=np.uint8)
    for frame in range(NUM_FRAMES):
        if frame % 25 == 0:
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
    imageio.mimsave('fireworks_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
