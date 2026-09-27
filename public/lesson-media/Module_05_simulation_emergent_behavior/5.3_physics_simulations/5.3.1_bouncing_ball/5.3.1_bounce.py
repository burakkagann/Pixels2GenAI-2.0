import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 480, 480
GRAVITY = 0.5
BOUNCE_DAMPING = 0.88        # share of speed kept after each bounce

class Ball:
    def __init__(self):
        self.x, self.y = 90.0, 90.0
        self.vx, self.vy = 5.2, 0.0
        self.radius = 18

    def step(self):
        self.vy += GRAVITY                            # integration: force -> velocity
        self.x += self.vx                             # velocity -> position
        self.y += self.vy
        if self.y + self.radius > HEIGHT:             # collision with the floor
            self.y = HEIGHT - self.radius             # clamp to wall
            self.vy = -self.vy * BOUNCE_DAMPING       # reflect velocity
        self.x %= WIDTH                               # off the right edge, back in on the left

ball = Ball()
frames = []
for _ in range(200):
    ball.step()
    img = Image.new('RGB', (WIDTH, HEIGHT), (16, 18, 30))
    x, y, r = ball.x, ball.y, ball.radius
    ImageDraw.Draw(img).ellipse([x - r, y - r, x + r, y + r], fill=(240, 220, 90))
    frames.append(np.array(img))

imageio.mimsave('bounce.gif', frames, fps=30)
