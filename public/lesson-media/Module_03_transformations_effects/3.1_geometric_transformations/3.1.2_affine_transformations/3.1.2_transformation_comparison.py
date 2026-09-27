import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

def create_arrow_shape():
    """Create an arrow-like shape to show orientation."""
    # Arrow pointing right, centered at origin
    points = np.array([
        [-40, -20],   # Back top
        [20, -20],    # Front top
        [20, -35],    # Upper arrow notch
        [50, 0],      # Arrow tip
        [20, 35],     # Lower arrow notch
        [20, 20],     # Front bottom
        [-40, 20],    # Back bottom
    ], dtype=np.float64)
    return points

def apply_affine_transform(points, matrix):
    """Apply 2x3 affine transformation matrix to points."""
    # Add homogeneous coordinate
    ones = np.ones((points.shape[0], 1))
    homogeneous = np.hstack([points, ones])
    # Apply transformation
    transformed = (matrix @ homogeneous.T).T
    return transformed

def draw_shape(ax, points, color, label, offset=(0, 0)):
    """Draw a filled polygon on matplotlib axes."""
    # Offset points for display
    display_points = points + np.array(offset)

    # Create closed polygon
    x_coords = np.append(display_points[:, 0], display_points[0, 0])
    y_coords = np.append(display_points[:, 1], display_points[0, 1])

    ax.fill(x_coords, y_coords, color=color, alpha=0.7, edgecolor='white', linewidth=2)
    ax.set_title(label, fontsize=14, fontweight='bold', color='white', pad=10)

# Create figure with 2x2 grid
fig, axes = plt.subplots(2, 2, figsize=(10, 10), facecolor='#1e1e2e')
fig.suptitle('Affine Transformation Types', fontsize=18, fontweight='bold',
             color='white', y=0.98)

# Get the base arrow shape
arrow = create_arrow_shape()

# Define transformation matrices (2x3 format: [a, b, tx; c, d, ty])
transformations = {
    'Original': np.array([
        [1, 0, 0],
        [0, 1, 0]
    ], dtype=np.float64),

    'Scaled (1.5x)': np.array([
        [1.5, 0, 0],
        [0, 1.5, 0]
    ], dtype=np.float64),

    'Sheared': np.array([
        [1, 0.5, 0],  # Horizontal shear
        [0, 1, 0]
    ], dtype=np.float64),

    'Rotated (30°)': np.array([
        [np.cos(np.radians(30)), -np.sin(np.radians(30)), 0],
        [np.sin(np.radians(30)), np.cos(np.radians(30)), 0]
    ], dtype=np.float64),
}

colors = ['#89b4fa', '#a6e3a1', '#fab387', '#f38ba8']

# Apply each transformation and plot
for ax, (name, matrix), color in zip(axes.flat, transformations.items(), colors):
    # Configure subplot
    ax.set_facecolor('#1e1e2e')
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, color='white')
    ax.axhline(y=0, color='white', linewidth=0.5, alpha=0.3)
    ax.axvline(x=0, color='white', linewidth=0.5, alpha=0.3)

    # Remove axis ticks for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])

    # Apply transformation
    transformed = apply_affine_transform(arrow, matrix)

    # Draw the transformed shape
    draw_shape(ax, transformed, color, name)

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save figure
plt.savefig('transformation_comparison.png', dpi=150, facecolor='#1e1e2e',
            bbox_inches='tight', pad_inches=0.2)
plt.close()
