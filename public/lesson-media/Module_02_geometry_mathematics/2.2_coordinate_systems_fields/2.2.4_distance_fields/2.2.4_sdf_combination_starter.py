import numpy as np
from PIL import Image

# =============================================================================
# Configuration
# =============================================================================
SIZE = 512
CENTER = SIZE // 2

# Create coordinate grids
Y, X = np.ogrid[0:SIZE, 0:SIZE]

# Shift coordinates so (0,0) is at center
x = X - CENTER
y = Y - CENTER

# =============================================================================
# TODO 1: Create your first shape (circle)
# =============================================================================
# Circle SDF formula: sqrt(x^2 + y^2) - radius
# Example: circle_sdf = np.sqrt(x**2 + y**2) - 100

circle_sdf = None  # TODO: Replace with your circle SDF

# =============================================================================
# TODO 2: Create your second shape (rectangle or another circle)
# =============================================================================
# Rectangle SDF formula: max(|x - cx| - half_width, |y - cy| - half_height)
# Example: rect_sdf = np.maximum(np.abs(x) - 80, np.abs(y) - 120)

second_shape_sdf = None  # TODO: Replace with your second shape SDF

# =============================================================================
# TODO 3: Combine the shapes
# =============================================================================
# Union: np.minimum(sdf1, sdf2) - combines both shapes
# Intersection: np.maximum(sdf1, sdf2) - keeps only overlap
# Subtraction: np.maximum(sdf1, -sdf2) - cuts shape2 from shape1

combined_sdf = None  # TODO: Replace with your combined SDF

# =============================================================================
# Visualization (provided - no changes needed)
# =============================================================================
if combined_sdf is not None:
    # Normalize for display
    normalized = np.clip(combined_sdf, -150, 150)
    normalized = ((normalized + 150) / 300 * 255).astype(np.uint8)

    # Save result
    output = Image.fromarray(normalized, mode='L')
    output.save('my_sdf_composition.png')
