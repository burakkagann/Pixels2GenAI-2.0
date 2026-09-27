
import numpy as np
from PIL import Image

# =============================================================================
# Configuration: Circle parameters (try changing these!)
# =============================================================================
CANVAS_SIZE = 512           # Width and height of the output image
CENTER_X = 256              # X coordinate of circle center
CENTER_Y = 256              # Y coordinate of circle center
RADIUS = 150                # Circle radius in pixels
CIRCLE_COLOR = [255, 128, 0]  # Orange color (RGB)

# =============================================================================
# Step 1: Create coordinate grids using np.ogrid
# =============================================================================
# np.ogrid creates two arrays: Y contains row indices, X contains column indices
# This allows us to calculate distances for ALL pixels at once (vectorized)
Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]

# =============================================================================
# Step 2: Calculate squared distance from each pixel to the center
# =============================================================================
# Using the Pythagorean theorem: distance² = (x - cx)² + (y - cy)²
# We use squared distance to avoid the costly sqrt() operation
square_distance = (X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2

# =============================================================================
# Step 3: Create a boolean mask for pixels inside the circle
# =============================================================================
# A pixel is inside the circle if its distance < radius
# Comparing squared values: distance² < radius² is equivalent to distance < radius
inside_circle = square_distance < RADIUS ** 2

# =============================================================================
# Step 4: Create canvas and apply the mask
# =============================================================================
# Start with a black canvas (all zeros)
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)

# Apply color only to pixels where the mask is True
canvas[inside_circle] = CIRCLE_COLOR

# =============================================================================
# Step 5: Save the result
# =============================================================================
output_image = Image.fromarray(canvas, mode='RGB')
output_image.save('circle.png')
