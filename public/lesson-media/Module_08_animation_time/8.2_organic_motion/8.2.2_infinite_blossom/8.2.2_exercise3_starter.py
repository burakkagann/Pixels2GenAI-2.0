import math, numpy as np
from PIL import Image, ImageDraw

class Particle:
    def __init__(self, angle_deg, dist, shape, color):
        self.angle = angle_deg
        self.dist = dist
        self.shape = shape       # 'tri', 'circle', or 'square'
        self.color = color

    def update(self):
        # TODO 1: same as before — rotate angle, decrease distance
        pass

    def draw(self, draw, centre):
        # TODO 2: dispatch on self.shape, draw the appropriate primitive
        pass

# Spawn loop: pick a random shape from ['tri', 'circle', 'square']
# and a random colour for each new particle.
