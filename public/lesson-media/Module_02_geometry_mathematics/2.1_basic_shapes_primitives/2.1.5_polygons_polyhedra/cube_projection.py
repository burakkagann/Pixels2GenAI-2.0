"""
cube_projection.py — wireframe cube rendered via orthographic projection.

The 8 cube vertices live in 3D; the 12 edges are pairs of vertex indices. To
draw the cube on a 2D canvas we drop the z-coordinate after rotating it
slightly so the projection shows three faces, not just one square silhouette.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


def draw_line(canvas, x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0)) + 1
    xs = np.linspace(x0, x1, n).round().astype(int)
    ys = np.linspace(y0, y1, n).round().astype(int)
    # Clip to canvas bounds (rotated cube can poke out slightly)
    h, w = canvas.shape
    inside = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
    canvas[ys[inside], xs[inside]] = 255


# Cube vertices in 3D, centred on the origin
vertices = np.array([
    [-1, -1, -1],
    [ 1, -1, -1],
    [ 1,  1, -1],
    [-1,  1, -1],
    [-1, -1,  1],
    [ 1, -1,  1],
    [ 1,  1,  1],
    [-1,  1,  1],
], dtype=float)

# Edges as pairs of vertex indices
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),       # bottom face
    (4, 5), (5, 6), (6, 7), (7, 4),       # top face
    (0, 4), (1, 5), (2, 6), (3, 7),       # verticals
]


def rotation_matrix(axis, theta):
    """Standard 3x3 rotation matrix about x, y, or z."""
    c, s = np.cos(theta), np.sin(theta)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == 'y':
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


# Rotate so we see three faces of the cube
R = rotation_matrix('y', np.radians(30)) @ rotation_matrix('x', np.radians(25))
rotated = vertices @ R.T

# Orthographic projection — drop the z-coordinate, scale, translate to canvas
CANVAS_SIZE = 400
scale = 100
cx, cy = CANVAS_SIZE // 2, CANVAS_SIZE // 2
projected = np.stack([
    (rotated[:, 0] * scale + cx).astype(int),
    (rotated[:, 1] * scale + cy).astype(int),
], axis=1)

canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)
for i, j in edges:
    x0, y0 = projected[i]
    x1, y1 = projected[j]
    draw_line(canvas, x0, y0, x1, y1)

Image.fromarray(canvas, mode='L').save('cube_projection.png')
