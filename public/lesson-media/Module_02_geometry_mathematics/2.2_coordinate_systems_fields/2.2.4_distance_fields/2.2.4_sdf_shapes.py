import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# =============================================================================
# Configuration
# =============================================================================
SIZE = 256              # Size of each sub-image
CENTER = SIZE // 2      # Center point (128, 128)
RADIUS = 80             # Circle radius
HALF_WIDTH = 60         # Rectangle half-width
HALF_HEIGHT = 80        # Rectangle half-height

# =============================================================================
# Step 1: Create coordinate grids (centered at origin for cleaner math)
# =============================================================================
Y, X = np.ogrid[0:SIZE, 0:SIZE]

# Shift coordinates so (0,0) is at center
x_centered = X - CENTER
y_centered = Y - CENTER

# =============================================================================
# Step 2: Define SDF functions for basic shapes
# =============================================================================

# Circle SDF: distance to center minus radius
# Negative inside, zero on edge, positive outside
circle_sdf = np.sqrt(x_centered**2 + y_centered**2) - RADIUS

# Rectangle SDF: uses the Chebyshev-like distance formula
# For axis-aligned boxes: max(|x| - width, |y| - height)
rect_sdf = np.maximum(np.abs(x_centered) - HALF_WIDTH,
                       np.abs(y_centered) - HALF_HEIGHT)

# =============================================================================
# Step 3: Combine shapes using boolean operations
# =============================================================================

# Union (OR): minimum of SDFs - creates combined shape
union_sdf = np.minimum(circle_sdf, rect_sdf)

# Intersection (AND): maximum of SDFs - creates overlap only
intersection_sdf = np.maximum(circle_sdf, rect_sdf)

# =============================================================================
# Step 4: Visualize as 2x2 grid
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(10, 10), dpi=100)

# Helper function to visualize SDF with consistent coloring
def visualize_sdf(ax, sdf, title):
    """Display SDF with blue (inside), white (boundary), red (outside)."""
    # Normalize for display: clamp to reasonable range
    display = np.clip(sdf, -100, 100)

    # Show with diverging colormap (blue=negative, white=0, red=positive)
    im = ax.imshow(display, cmap='RdBu', vmin=-100, vmax=100)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')

    # Add contour at boundary (where SDF = 0)
    ax.contour(sdf, levels=[0], colors='black', linewidths=2)

    return im

# Create the 2x2 visualization
visualize_sdf(axes[0, 0], circle_sdf, 'Circle SDF')
visualize_sdf(axes[0, 1], rect_sdf, 'Rectangle SDF')
visualize_sdf(axes[1, 0], union_sdf, 'Union (min)')
visualize_sdf(axes[1, 1], intersection_sdf, 'Intersection (max)')

# Add colorbar
fig.subplots_adjust(right=0.85)
cbar_ax = fig.add_axes([0.88, 0.15, 0.03, 0.7])
cbar = fig.colorbar(plt.cm.ScalarMappable(cmap='RdBu',
                    norm=plt.Normalize(vmin=-100, vmax=100)),
                    cax=cbar_ax)
cbar.set_label('Signed Distance', fontsize=12)
cbar.set_ticks([-100, 0, 100])
cbar.set_ticklabels(['Inside (-100)', '0 (boundary)', 'Outside (+100)'])

plt.suptitle('Signed Distance Functions for Basic Shapes', fontsize=16, fontweight='bold', y=0.98)
plt.savefig('sdf_shapes.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
