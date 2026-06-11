
import numpy as np
from PIL import Image

# =============================================================================
# Configuration
# =============================================================================
CANVAS_SIZE = 512
CENTER_X = 256
CENTER_Y = 256

# Define 5 radii from largest to smallest (even spacing of 40 pixels)
RADII = [200, 160, 120, 80, 40]

# Alternating colors: red, white, red, white, red
RED = [255, 0, 0]
WHITE = [255, 255, 255]
COLORS = [RED, WHITE, RED, WHITE, RED]

# =============================================================================
# Step 1: Create coordinate grids
# =============================================================================
# np.ogrid creates efficient broadcasting arrays for vectorized operations
Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]

# =============================================================================
# Step 2: Calculate squared distance from center
# =============================================================================
# This only needs to be computed once since all circles share the same center
square_distance = (X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2

# =============================================================================
# Step 3: Create canvas (start with black background)
# =============================================================================
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)

# =============================================================================
# Step 4: Draw circles from largest to smallest
# =============================================================================
# Critical insight: We draw largest first so smaller circles paint OVER them
# This creates the layered bulls-eye effect
for i, (radius, color) in enumerate(zip(RADII, COLORS)):
    # Create mask for pixels inside this circle
    inside_circle = square_distance < radius ** 2

    # Apply color to all pixels inside this circle
    canvas[inside_circle] = color

    # Debug output to track progress
    print(f"Circle {i+1}: radius={radius}, color=RGB{tuple(color)}")

# =============================================================================
# Step 5: Save the result
# =============================================================================
output_image = Image.fromarray(canvas, mode='RGB')
output_image.save('concentric_circles.png')
