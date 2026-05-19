import numpy as np
from PIL import Image

# =============================================================================
# Configuration: Distance field parameters (try changing these!)
# =============================================================================
CANVAS_SIZE = 512           # Width and height of the output image
CENTER_X = 256              # X coordinate of the reference point
CENTER_Y = 256              # Y coordinate of the reference point

# =============================================================================
# Step 1: Create coordinate grids using np.ogrid
# =============================================================================
# np.ogrid creates arrays for Y (rows) and X (columns)
# This allows vectorized distance calculation for ALL pixels at once
Y, X = np.ogrid[0:CANVAS_SIZE, 0:CANVAS_SIZE]

# =============================================================================
# Step 2: Calculate the distance from each pixel to the center point
# =============================================================================
# Using the Euclidean distance formula: d = sqrt((x - cx)^2 + (y - cy)^2)
# Unlike circle drawing, we keep the actual distance values (not just inside/outside)
distance_field = np.sqrt((X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2)

# =============================================================================
# Step 3: Normalize distance values to 0-255 for visualization
# =============================================================================
# Find the maximum distance (corner to center) for normalization
max_distance = distance_field.max()

# Scale values: 0 (at center) to 255 (at farthest point)
# Closest pixels are dark (low values), farthest are bright (high values)
normalized = (distance_field / max_distance * 255).astype(np.uint8)

# =============================================================================
# Step 4: Save the result as a grayscale image
# =============================================================================
output_image = Image.fromarray(normalized, mode='L')
output_image.save('simple_distance_field.png')
