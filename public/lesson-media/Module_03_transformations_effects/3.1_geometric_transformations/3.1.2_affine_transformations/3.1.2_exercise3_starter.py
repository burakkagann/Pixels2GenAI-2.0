import numpy as np
from PIL import Image, ImageDraw

def translate(tx, ty):
    return np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], dtype=np.float64)

def scale(s):
    return np.array([[s, 0, 0], [0, s, 0], [0, 0, 1]], dtype=np.float64)

def rotate(deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)

def apply(points, m):
    homo = np.hstack([points, np.ones((len(points), 1))])
    return (m @ homo.T).T[:, :2]

SIZE = 500; CENTER = SIZE // 2
canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8) + 20
img = Image.fromarray(canvas); draw = ImageDraw.Draw(img)

base = np.array([[-15, -15], [15, -15], [15, 15], [-15, 15]], dtype=np.float64)

for i in range(24):
    # TODO 1: derive angle, shrink factor, and outward distance from i.
    # angle = ...; shrink = ...; distance = ...

    # TODO 2: target position along a spiral (polar → cartesian).
    # tx = CENTER + distance * cos(2 * angle in radians)
    # ty = CENTER + distance * sin(2 * angle in radians)

    # TODO 3: compose the matrix and apply it to base.
    # combined = translate(tx, ty) @ scale(shrink) @ rotate(angle)

    # TODO 4: pick a colour from a blue → orange gradient and draw the polygon.

img.save('spiral.png')
