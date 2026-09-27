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
    angle    = i * 15
    shrink   = max(1.0 - 0.025 * i, 0.3)
    distance = 50 + 6 * i

    spiral = np.radians(2 * angle)
    tx = CENTER + distance * np.cos(spiral)
    ty = CENTER + distance * np.sin(spiral)

    combined = translate(tx, ty) @ scale(shrink) @ rotate(angle)
    pts = apply(base, combined).astype(int)

    t = i / 23
    color = (int(70 + 180 * t), int(130 - 50 * t), int(200 - 150 * t))
    draw.polygon([tuple(p) for p in pts], fill=color, outline=(255, 255, 255))

img.save('spiral.png')
