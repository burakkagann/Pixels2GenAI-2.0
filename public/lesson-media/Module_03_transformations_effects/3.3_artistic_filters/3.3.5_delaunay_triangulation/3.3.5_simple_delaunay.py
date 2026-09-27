import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

np.random.seed(42)                    # fixed seed: the same 50 points every run
points = np.random.rand(50, 2) * 400

tri = Delaunay(points)

plt.figure(figsize=(8, 8))
plt.triplot(points[:, 0], points[:, 1], tri.simplices,
            color='steelblue', linewidth=0.8)
plt.plot(points[:, 0], points[:, 1], 'o', color='coral', markersize=6)
plt.title(f'Delaunay Triangulation (50 points, {len(tri.simplices)} triangles)')
plt.axis('equal'); plt.axis('off')
plt.tight_layout()
plt.savefig('simple_delaunay.png', dpi=150, bbox_inches='tight', facecolor='white')
