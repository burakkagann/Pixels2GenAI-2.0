
import numpy as np
from PIL import Image

# =============================================================================
# Configuration
# =============================================================================
CANVAS_SIZE = 512
CENTER_X = 256
CENTER_Y = 256

# TODO: Define 5 radii for your concentric circles (from largest to smallest)
# Hint: Try spacing them evenly, e.g., 200, 160, 120, 80, 40
RADII = [200, 160, 120, 80, 40]

# TODO: Define 5 colors for alternating red and white
# Hint: Red = [255, 0, 0], White = [255, 255, 255]
COLORS = [
    # Fill in the colors here (red, white, red, white, red)
]

# =============================================================================
# Step 1: Create coordinate grids
# =============================================================================
Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]

# =============================================================================
# Step 2: Calculate squared distance from center (same for all circles)
# =============================================================================
square_distance = (X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2

# =============================================================================
# Step 3: Create canvas
# =============================================================================
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)

# =============================================================================
# Step 4: Draw circles from largest to smallest
# =============================================================================
# TODO: Loop through each radius and color, drawing circles
# Hint: Use a for loop with zip(RADII, COLORS)
#
# for radius, color in zip(RADII, COLORS):
#     # Create mask for this circle
#     # Apply color to canvas where mask is True

# =============================================================================
# Step 5: Save the result
# =============================================================================
output_image = Image.fromarray(canvas, mode='RGB')
output_image.save('concentric_circles.png')
