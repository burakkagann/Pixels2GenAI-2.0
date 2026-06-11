import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay
from PIL import Image

# Image dimensions
WIDTH, HEIGHT = 400, 400

# ============================================================
# STEP 1: Generate a procedural source image
# Creates a colorful gradient with sun-like circular pattern
# ============================================================

def create_procedural_image(width, height):
    """Create a colorful procedural image with gradient and circles."""
    image = np.zeros((height, width, 3), dtype=np.uint8)

    # Create coordinate grids
    y, x = np.ogrid[:height, :width]

    # Background gradient (sunset-like colors)
    image[:, :, 0] = np.clip(255 - y * 0.4, 0, 255).astype(np.uint8)  # Red fading
    image[:, :, 1] = np.clip(100 + np.sin(x * 0.02) * 80, 0, 255).astype(np.uint8)  # Green wave
    image[:, :, 2] = np.clip(50 + y * 0.5, 0, 255).astype(np.uint8)  # Blue increasing

    # Add sun circle
    cx, cy = width // 2, height // 3
    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
    sun_mask = dist < 80
    image[sun_mask, 0] = 255
    image[sun_mask, 1] = np.clip(200 + (80 - dist[sun_mask]) * 0.5, 0, 255).astype(np.uint8)
    image[sun_mask, 2] = 50

    # Add a second smaller circle
    cx2, cy2 = width // 4, height * 2 // 3
    dist2 = np.sqrt((x - cx2)**2 + (y - cy2)**2)
    circle_mask = dist2 < 50
    image[circle_mask, 0] = 100
    image[circle_mask, 1] = 200
    image[circle_mask, 2] = 255

    return image

source_image = create_procedural_image(WIDTH, HEIGHT)

# ============================================================
# STEP 2: Generate sample points
# ============================================================

np.random.seed(42)
num_points = 150  # Adjust for more/less detail

# Generate random (x, y) coordinates within image bounds
points = np.random.rand(num_points, 2) * [WIDTH, HEIGHT]

# Add corner points to ensure triangulation covers entire image
corners = np.array([
    [0, 0],
    [WIDTH, 0],
    [WIDTH, HEIGHT],
    [0, HEIGHT]
])
points = np.vstack([points, corners])

# Add edge points for better coverage
edge_points = np.array([
    [WIDTH/2, 0],       # Top middle
    [WIDTH/2, HEIGHT],  # Bottom middle
    [0, HEIGHT/2],      # Left middle
    [WIDTH, HEIGHT/2]   # Right middle
])
points = np.vstack([points, edge_points])

# ============================================================
# STEP 3: Compute Delaunay triangulation
# ============================================================

triangulation = Delaunay(points)

# ============================================================
# STEP 4: Sample colors from source image for each triangle
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
    # Calculate the centroid (average of three vertices)
    centroid = np.mean(vertices, axis=0)
    cx, cy = centroid

    # Clamp to valid image coordinates
    cx = np.clip(int(cx), 0, source.shape[1] - 1)
    cy = np.clip(int(cy), 0, source.shape[0] - 1)

    # Get the color at the centroid location
    # Note: image indexing is [y, x], not [x, y]!
    color = source[cy, cx]

    # Normalize color to [0, 1] range for matplotlib
    return color / 255.0

# ============================================================
# STEP 5: Build the triangles and colors arrays
# ============================================================

triangles = []
colors = []

for simplex in triangulation.simplices:
    # Get the triangle vertices
    triangle = points[simplex]
    triangles.append(triangle)

    # Get the color from the source image
    color = get_triangle_color(source_image, triangle)
    colors.append(color)

# ============================================================
# STEP 6: Create the visualization
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Left: Original image
axes[0].imshow(source_image)
axes[0].set_title('Original Procedural Image', fontsize=12)
axes[0].axis('off')

# Right: Low-poly version
collection = PolyCollection(triangles, facecolors=colors,
                           edgecolors='none')  # No edges for smoother look
axes[1].add_collection(collection)
axes[1].set_xlim(0, WIDTH)
axes[1].set_ylim(HEIGHT, 0)  # Flip Y axis to match image coordinates
axes[1].set_aspect('equal')
axes[1].set_title(f'Low-Poly Art ({num_points} points, {len(triangulation.simplices)} triangles)',
                  fontsize=12)
axes[1].axis('off')

plt.tight_layout()
plt.savefig('lowpoly_art_output.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

# Also save just the low-poly image
fig2, ax2 = plt.subplots(figsize=(8, 8))
collection2 = PolyCollection(triangles, facecolors=colors, edgecolors='none')
ax2.add_collection(collection2)
ax2.set_xlim(0, WIDTH)
ax2.set_ylim(HEIGHT, 0)
ax2.set_aspect('equal')
ax2.axis('off')
plt.tight_layout()
plt.savefig('lowpoly_art_single.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none', pad_inches=0)
plt.close()

print("Low-poly art generation complete!")
print(f"Number of sample points: {len(points)}")
print(f"Number of triangles: {len(triangulation.simplices)}")
print("Output saved as: lowpoly_art_output.png")
print("Single image saved as: lowpoly_art_single.png")
