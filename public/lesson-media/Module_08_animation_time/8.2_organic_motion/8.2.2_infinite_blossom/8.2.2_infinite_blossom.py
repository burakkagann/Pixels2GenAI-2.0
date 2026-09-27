import math
import numpy as np
from PIL import Image, ImageDraw

INNER, CANVAS, SPAWN_R, FRAMES = 800, 600, 320, 180

class Petal:
    def __init__(self, angle_deg, dist):
        self.angle = angle_deg
        self.dist = dist
    def update(self):
        self.angle = (self.angle + 1.2) % 360
        self.dist -= 1.5
    def polar(self, ang, d):
        r = math.radians(ang)
        return int(math.cos(r) * d), int(math.sin(r) * d)
    def draw(self, draw):
        m = 1.2 + self.dist / 280
        v = [self.polar(self.angle, self.dist),
             self.polar(self.angle - 30, self.dist * m),
             self.polar(self.angle + 30, self.dist * m)]
        ox, oy = INNER // 2, INNER // 2
        d = max(0, min(1, self.dist / SPAWN_R))   # red at the centre, orange at the rim
        col = (255, int(60 + 110 * d), int(40 + 60 * d))
        draw.polygon([(x + ox, y + oy) for x, y in v], fill=col)

def create_three(dist, angle_offset):
    # Three petals 120° apart: the blossom's three-fold symmetry
    return [Petal(angle_offset + a, dist) for a in (0, 120, 240)]

rng = np.random.default_rng(5)
petals = []
for dist in range(40, SPAWN_R, 40):              # start with rings already in flight
    petals += create_three(dist, rng.uniform(0, 360))

margin = (INNER - CANVAS) // 2                   # render large, keep the centre
frames = []
for f in range(FRAMES):
    img = Image.new('RGB', (INNER, INNER), (20, 22, 30))
    draw = ImageDraw.Draw(img)
    if f % 12 == 0:                              # a new triplet at the rim every 12 frames
        petals += create_three(SPAWN_R, rng.uniform(0, 360))
    for p in petals:
        p.update()
        p.draw(draw)
    petals = [p for p in petals if p.dist > 0]   # drop petals that reached the centre
    frames.append(img.crop((margin, margin, margin + CANVAS, margin + CANVAS)))

frames[0].save('infinite_blossom.gif', save_all=True, append_images=frames[1:],
               duration=50, loop=0, optimize=True)
