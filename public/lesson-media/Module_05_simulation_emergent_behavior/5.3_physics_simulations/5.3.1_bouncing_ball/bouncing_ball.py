"""
bouncing_ball.py - A bouncing ball under gravity, elastic collisions with
walls (with damping), and an optional motion trail. Renders frames as a
GIF instead of an interactive window so the script is portable.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 480
NUM_FRAMES = 200
FPS = 30

GRAVITY = 0.5
BOUNCE_DAMPING = 0.88     # energy retained per wall bounce
INITIAL_POS = (90, 90)
INITIAL_VEL = (5.2, 0.0)
RADIUS = 18

BG = (16, 18, 30)
BALL_COLOUR = (240, 220, 90)
TRAIL_COLOUR = (220, 160, 60)
TRAIL_LEN = 30
# ----------------------------


class Ball:
    def __init__(self, position, velocity, radius):
        self.x, self.y = position
        self.vx, self.vy = velocity
        self.radius = radius
        self.trail = []

    def step(self):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * BOUNCE_DAMPING
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * BOUNCE_DAMPING

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy * BOUNCE_DAMPING
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy = -self.vy * BOUNCE_DAMPING

        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_LEN:
            self.trail.pop(0)


def render(ball):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    for i, (tx, ty) in enumerate(ball.trail):
        fade = (i + 1) / len(ball.trail)
        r = int(ball.radius * (0.3 + 0.7 * fade))
        colour = tuple(int(TRAIL_COLOUR[k] * fade) for k in range(3))
        draw.ellipse([tx - r, ty - r, tx + r, ty + r], fill=colour)

    draw.ellipse(
        [ball.x - ball.radius, ball.y - ball.radius,
         ball.x + ball.radius, ball.y + ball.radius],
        fill=BALL_COLOUR,
    )
    return np.array(img)


def main():
    ball = Ball(INITIAL_POS, INITIAL_VEL, RADIUS)
    frames = []
    for frame in range(NUM_FRAMES):
        ball.step()
        img = render(ball)
        frames.append(img)
        if frame == NUM_FRAMES // 2:
            Image.fromarray(img).save('bouncing_ball_frame.png')

    imageio.mimsave('bouncing_ball.gif', frames, fps=FPS)
    print(f'Wrote bouncing_ball.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
