
import numpy as np
from PIL import Image

# =============================================================================
# STEP 1: Create a colorful source image
# =============================================================================
# We'll create a geometric pattern that shows color changes clearly
height, width = 200, 200
source = np.zeros((height, width, 3), dtype=np.uint8)

# Create a pattern with diagonal stripes and a central circle
cx, cy = width // 2, height // 2
radius = 60

for y in range(height):
    for x in range(width):
        # Check if inside circle
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)

        if dist_from_center < radius:
            # Inside circle: warm colors
            source[y, x] = [255, 150, 50]  # Orange
        else:
            # Outside: diagonal stripe pattern
            stripe = (x + y) // 20 % 3
            if stripe == 0:
                source[y, x] = [50, 100, 200]   # Blue
            elif stripe == 1:
                source[y, x] = [100, 200, 100]  # Green
            else:
                source[y, x] = [200, 80, 150]   # Pink

# =============================================================================
# STEP 2: Define four distinct color variations
# =============================================================================
# Choose permutations that create maximum visual contrast
variations = [
    [0, 1, 2],  # Original: Orange circle, blue/green/pink stripes
    [1, 2, 0],  # Rotate left: Cyan circle, different stripe colors
    [2, 0, 1],  # Rotate right: Blue-ish circle, warm stripes
    [2, 1, 0],  # Swap R-B: Teal circle, inverted stripes
]

# =============================================================================
# STEP 3: Create the 2x2 grid canvas
# =============================================================================
grid_height = height * 2
grid_width = width * 2
canvas = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)

# =============================================================================
# STEP 4: Place each variation in its quadrant
# =============================================================================
# Top-left: Original
canvas[0:height, 0:width] = source[:, :, variations[0]]

# Top-right: First rotation
canvas[0:height, width:grid_width] = source[:, :, variations[1]]

# Bottom-left: Second rotation
canvas[height:grid_height, 0:width] = source[:, :, variations[2]]

# Bottom-right: Swap
canvas[height:grid_height, width:grid_width] = source[:, :, variations[3]]

# =============================================================================
# STEP 5: Save the final pop art piece
# =============================================================================
output = Image.fromarray(canvas, mode='RGB')
output.save('warhol_solution.png')

print("Saved warhol_solution.png!")
print("\nChannel arrangements used:")
print("  Top-left:     [R, G, B] - Original colors")
print("  Top-right:    [G, B, R] - Rotate left")
print("  Bottom-left:  [B, R, G] - Rotate right")
print("  Bottom-right: [B, G, R] - Swap R and B")
