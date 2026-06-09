import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay
from PIL import Image

# Image dimensions
WIDTH, HEIGHT = 400, 400

# ============================================================
# STEP 1: Generate a procedural source image (provided)
# This creates a colorful gradient with circular patterns
# ============================================================

def create_procedural_image(width, height):
    """Create a colorful procedural image with gradient and circles."""
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Create coordinate grids
    y, x = np.ogrid[:height, :width]

    # Background gradient (sunset-like)
    image[:, :, 0] = np.clip(255 - y * 0.4, 0, 255).astype(np.uint8)  # Red
    image[:, :, 1] = np.clip(100 + np.sin(x * 0.02) * 80, 0, 255).astype(np.uint8)  # Green
    image[:, :, 2] = np.clip(50 + y * 0.5, 0, 255).astype(np.uint8)  # Blue

    # Add circular patterns
    cx, cy = width // 2, height // 3
    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    sun_mask = dist < 80
    image[sun_mask, 0] = 255
    image[sun_mask, 1] = np.clip(200 + (80 - dist[sun_mask]) * 0.5, 0, 255).astype(np.uint8)
    image[sun_mask, 2] = 50

    return image

source_image = create_procedural_image(WIDTH, HEIGHT)

# ============================================================
# STEP 2: Generate sample points
# TODO: Create random points across the image
# ============================================================

np.random.seed(42)
num_points = 150  # Adjust for more/less detail

# TODO: Generate random (x, y) coordinates within image bounds
# Hint: Use np.random.rand() and multiply by WIDTH/HEIGHT
points = None  # Replace with your code

# TODO: Add corner points to ensure triangulation covers entire image
# Hint: corners = np.array([[0, 0], [WIDTH, 0], ...])

# ============================================================
# STEP 3: Compute Delaunay triangulation
# TODO: Use scipy.spatial.Delaunay on your points
# ============================================================

triangulation = None  # Replace with your code

# ============================================================
# STEP 4: Sample colors from source image for each triangle
# TODO: For each triangle, calculate the average color
# ============================================================

def get_triangle_color(source, vertices):
    """
    Get the average color of pixels inside a triangle.

    For simplicity, we sample the color at the triangle's centroid.

    Args:
        source: The source image array (H, W, 3)
        vertices: Triangle vertices as (3, 2) array of (x, y) coords

    Returns:
        RGB color as (3,) array normalized to [0, 1]
    """
    # TODO: Calculate the centroid (average of three vertices)
    # centroid = ...

    # TODO: Get the color at the centroid location
    # Remember: image indexing is [y, x], not [x, y]!
    # color = source[int(cy), int(cx)]

    # TODO: Normalize color to [0, 1] range for matplotlib
    # return color / 255.0

    pass  # Remove this and add your code

# ============================================================
# STEP 5: Build and render the low-poly visualization
# TODO: Create PolyCollection with triangles and their colors
# ============================================================

# Collect triangles and colors
triangles = []
colors = []

# TODO: Loop through triangulation.simplices
# For each simplex:
#   1. Get the triangle vertices from points
#   2. Get the color using get_triangle_color()
#   3. Append to triangles and colors lists

# ============================================================
# STEP 6: Create the visualization
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Left: Original image
axes[0].imshow(source_image)
axes[0].set_title('Original Procedural Image', fontsize=12)
axes[0].axis('off')

# Right: Low-poly version
# TODO: Add PolyCollection to axes[1]
# collection = PolyCollection(triangles, facecolors=colors, ...)
# axes[1].add_collection(collection)

axes[1].set_xlim(0, WIDTH)
axes[1].set_ylim(HEIGHT, 0)  # Flip Y axis to match image coordinates
axes[1].set_aspect('equal')
axes[1].set_title(f'Low-Poly Art ({num_points} points)', fontsize=12)
axes[1].axis('off')

plt.tight_layout()
plt.savefig('lowpoly_art_output.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Low-poly art generation complete!")
print(f"Output saved as: lowpoly_art_output.png")
