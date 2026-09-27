import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay

W, H = 400, 400
rng = np.random.default_rng(42)

y, x = np.ogrid[:H, :W]
source = np.zeros((H, W, 3), dtype=np.uint8)
source[..., 0] = np.clip(255 - y * 0.4, 0, 255)
source[..., 1] = np.clip(100 + np.sin(x * 0.02) * 80, 0, 255)
source[..., 2] = np.clip(50 + y * 0.5, 0, 255)

dist = np.sqrt((x - W // 2) ** 2 + (y - H // 3) ** 2)
source[dist < 80] = [255, 200, 80]

points = rng.random((150, 2)) * [W, H]
corners = np.array([[0, 0], [W, 0], [W, H], [0, H]])
edges   = np.array([[W/2, 0], [W/2, H], [0, H/2], [W, H/2]])
points  = np.vstack([points, corners, edges])

tri = Delaunay(points)

def tri_colour(simplex):
    verts = points[simplex]
    cx, cy = verts.mean(axis=0)
    cx = int(np.clip(cx, 0, W - 1)); cy = int(np.clip(cy, 0, H - 1))
    return source[cy, cx] / 255.0

triangles = [points[s]   for s in tri.simplices]
colours   = [tri_colour(s) for s in tri.simplices]

fig, ax = plt.subplots(figsize=(8, 8))
ax.add_collection(PolyCollection(triangles, facecolors=colours, edgecolors='none'))
ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.set_aspect('equal'); ax.axis('off')
plt.savefig('lowpoly.png', dpi=150, bbox_inches='tight', pad_inches=0)
