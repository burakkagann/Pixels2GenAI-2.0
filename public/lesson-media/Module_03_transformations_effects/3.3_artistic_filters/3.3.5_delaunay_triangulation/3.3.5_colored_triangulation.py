import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay

# Step 1: Generate random points
np.random.seed(42)
num_points = 100
width, height = 500, 500
points = np.random.rand(num_points, 2) * [width, height]

# Add corner points to cover the entire canvas
corners = np.array([[0, 0], [width, 0], [width, height], [0, height]])
points = np.vstack([points, corners])

# Step 2: Compute Delaunay triangulation
triangulation = Delaunay(points)

# Step 3: Create filled triangles with random colors
triangles = []
colors = []

for simplex in triangulation.simplices:
    # Get the three vertices of each triangle
    triangle = points[simplex]
    triangles.append(triangle)

    # Assign a random color (RGB)
    color = np.random.rand(3)
    colors.append(color)

# Step 4: Create the visualization
fig, ax = plt.subplots(figsize=(8, 8))

# Use PolyCollection for efficient rendering of many polygons
collection = PolyCollection(triangles, facecolors=colors,
                           edgecolors='white', linewidths=0.5)
ax.add_collection(collection)

ax.set_xlim(0, width)
ax.set_ylim(0, height)
ax.set_aspect('equal')
ax.axis('off')
ax.set_title(f'Colored Delaunay Triangulation\n{num_points} points, {len(triangulation.simplices)} triangles',
             fontsize=14, pad=10)

plt.tight_layout()
plt.savefig('colored_triangulation.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Colored triangulation complete!")
print(f"Number of points: {num_points + 4} (including corners)")
print(f"Number of triangles: {len(triangulation.simplices)}")
print("Output saved as: colored_triangulation.png")
