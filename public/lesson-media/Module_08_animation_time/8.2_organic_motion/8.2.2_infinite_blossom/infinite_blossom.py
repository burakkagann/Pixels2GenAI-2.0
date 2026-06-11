"""
infinite_blossom.py — petals spawn at the canvas edge in polar coordinates,
rotate as they fall toward the centre, and disappear when they arrive.
New petals spawn continuously so the animation has no start or end.

This is a Pillow rewrite of the original OpenCV implementation: same
geometry, no real-time display, output is an infinitely-looping animated
GIF.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


CANVAS = 600           # final cropped canvas size
INNER = 800            # render canvas (larger; we crop the result)
SPAWN_RADIUS = 320
FRAMES = 180
SEED = 5


class Petal:
    """A petal located at (angle, dist) in polar coordinates around the centre."""

    __slots__ = ('angle', 'dist')

    def __init__(self, angle_deg, dist):
        self.angle = angle_deg
        self.dist = dist

    def update(self):
        # Spiral inward — rotate 1.2° per frame, lose 1.5 px of distance
        self.angle = (self.angle + 1.2) % 360
        self.dist -= 1.5

    def polar_to_xy(self, angle_deg, dist):
        r = math.radians(angle_deg)
        return int(math.cos(r) * dist), int(math.sin(r) * dist)

    def draw(self, draw):
        ang_outer_mult = 1.2 + self.dist / 280
        x1, y1 = self.polar_to_xy(self.angle, self.dist)
        x2, y2 = self.polar_to_xy(self.angle - 30, self.dist * ang_outer_mult)
        x3, y3 = self.polar_to_xy(self.angle + 30, self.dist * ang_outer_mult)

        # Colour ranges from red near centre to orange at the edges
        d_norm = max(0, min(1, self.dist / SPAWN_RADIUS))
        col = (255, int(60 + 110 * d_norm), int(40 + 60 * d_norm))

        # Centre on the inner canvas
        ox, oy = INNER // 2, INNER // 2
        draw.polygon(
            [(x1 + ox, y1 + oy), (x2 + ox, y2 + oy), (x3 + ox, y3 + oy)],
            fill=col,
        )


def create_three(dist, angle_offset_deg):
    """Spawn 3 petals 120° apart at a given distance."""
    return [
        Petal(angle_offset_deg + a, dist) for a in (0, 120, 240)
    ]


def main():
    rng = np.random.default_rng(SEED)
    petals = []
    # Seed a stack of petals at multiple radii so the animation starts mid-flow
    for dist in range(40, SPAWN_RADIUS, 40):
        petals += create_three(dist, rng.uniform(0, 360))

    # Crop bounds (centre square of inner canvas)
    crop_box = (
        (INNER - CANVAS) // 2,
        (INNER - CANVAS) // 2,
        (INNER - CANVAS) // 2 + CANVAS,
        (INNER - CANVAS) // 2 + CANVAS,
    )

    frames = []
    for f in range(FRAMES):
        img = Image.new('RGB', (INNER, INNER), (20, 22, 30))
        draw = ImageDraw.Draw(img)

        # Spawn fresh petals every 12 frames
        if f % 12 == 0:
            petals += create_three(SPAWN_RADIUS, rng.uniform(0, 360))

        # Update and render all petals
        for p in petals:
            p.update()
            p.draw(draw)

        # Drop petals that have arrived at the centre
        petals = [p for p in petals if p.dist > 0]

        frames.append(img.crop(crop_box))

    frames[0].save(
        'infinite_blossom.gif',
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        optimize=True,
    )
    frames[FRAMES // 2].save('blossom_still.png')
    print(f"Saved infinite_blossom.gif — {FRAMES} frames, ~{len(petals)} live petals")


if __name__ == '__main__':
    main()
