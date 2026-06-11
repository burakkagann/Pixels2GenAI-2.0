"""
bouncing_ball_starter.py - Exercise 3 scaffold.

The render loop is wired up. You implement gravity, the per-frame integration
step, and the wall-collision response inside `Ball.step()`.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 480, 480
NUM_FRAMES = 180
FPS = 30
GRAVITY = 0.5
BOUNCE_DAMPING = 0.88
RADIUS = 18
BG = (16, 18, 30)
BALL_COLOUR = (240, 220, 90)


class Ball:
    def __init__(self, position, velocity):
        self.x, self.y = position
        self.vx, self.vy = velocity
        self.radius = RADIUS

    def step(self):
        # TODO 1: apply gravity by adding GRAVITY to self.vy.
        # TODO 2: advance position by velocity.
        # TODO 3: on each of the four walls, if the ball has crossed,
        #         clamp the position back to the wall and flip the
        #         corresponding velocity component, multiplied by
        #         BOUNCE_DAMPING.
        pass


def render(ball):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    draw.ellipse(
        [ball.x - ball.radius, ball.y - ball.radius,
         ball.x + ball.radius, ball.y + ball.radius],
        fill=BALL_COLOUR,
    )
    return np.array(img)


def main():
    ball = Ball((90, 90), (5.2, 0.0))
    frames = []
    for _ in range(NUM_FRAMES):
        ball.step()
        frames.append(render(ball))
    imageio.mimsave('bouncing_ball_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
