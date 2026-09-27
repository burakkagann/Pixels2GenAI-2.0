import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay

W, H = 400, 400
rng = np.random.default_rng(42)

# TODO 1: build a procedural source image (H, W, 3) uint8 with a sunset gradient
#         and a sun-like circle. See hint for one approach.

# TODO 2: sample 150 random points, then append the 4 corners and 4 edge midpoints.

# TODO 3: compute the Delaunay triangulation.

# TODO 4: per triangle: sample the centroid colour from the source.

# TODO 5: render with PolyCollection; flip the y-axis to match image coords.

plt.savefig('lowpoly.png', dpi=150, bbox_inches='tight', pad_inches=0)
