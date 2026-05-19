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
# Step 1: Create outer circle (radius 180)
# =============================================================================
outer_circle_sdf = np.sqrt(x**2 + y**2) - 180

# =============================================================================
# Step 2: Create inner circle (radius 100) - we'll subtract this
# =============================================================================
inner_circle_sdf = np.sqrt(x**2 + y**2) - 100

# =============================================================================
# Step 3: Create a ring by subtracting inner from outer
# =============================================================================
# Subtraction formula: max(shape1, -shape2)
# This keeps points that are inside shape1 AND outside shape2
ring_sdf = np.maximum(outer_circle_sdf, -inner_circle_sdf)

# =============================================================================
# Step 4: Create a vertical rectangle
# =============================================================================
rect_sdf = np.maximum(np.abs(x) - 30, np.abs(y) - 200)

# =============================================================================
# Step 5: Combine ring and rectangle using union
# =============================================================================
# Union: min(sdf1, sdf2) - combines both shapes
combined_sdf = np.minimum(ring_sdf, rect_sdf)

# =============================================================================
# Step 6: Visualize with smooth gradient coloring
# =============================================================================
# Normalize for display: clamp to visible range
normalized = np.clip(combined_sdf, -150, 150)
normalized = ((normalized + 150) / 300 * 255).astype(np.uint8)

# Save as grayscale
output = Image.fromarray(normalized, mode='L')
output.save('sdf_combination_solution.png')

