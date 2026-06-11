import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay

# Step 1: Generate random points in 2D space
# Using a fixed seed ensures reproducible results for learning
np.random.seed(42)
num_points = 50
points = np.random.rand(num_points, 2) * 400  # 50 points in 400x400 space

# Step 2: Compute Delaunay triangulation
# This creates triangles that maximize the minimum angle (no thin slivers)
triangulation = Delaunay(points)

# Step 3: Visualize the triangulation
plt.figure(figsize=(8, 8))
plt.triplot(points[:, 0], points[:, 1], triangulation.simplices,
            color='steelblue', linewidth=0.8)
plt.plot(points[:, 0], points[:, 1], 'o', color='coral', markersize=6)
plt.title(f'Delaunay Triangulation ({num_points} points, {len(triangulation.simplices)} triangles)')
plt.axis('equal')
plt.axis('off')
plt.tight_layout()
plt.savefig('simple_delaunay.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Delaunay triangulation complete!")
print(f"Number of points: {num_points}")
print(f"Number of triangles: {len(triangulation.simplices)}")
print("Output saved as: simple_delaunay.png")
