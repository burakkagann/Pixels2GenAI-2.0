import numpy as np
from PIL import Image

# =============================================================================
# STEP 1: Create the source image (provided for you)
# =============================================================================
height, width = 200, 200
source = np.zeros((height, width, 3), dtype=np.uint8)

# Create a pattern with diagonal stripes and a central circle
cx, cy = width // 2, height // 2
radius = 60

for y in range(height):
    for x in range(width):
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)

        if dist_from_center < radius:
            source[y, x] = [255, 150, 50]  # Orange circle
        else:
            stripe = (x + y) // 20 % 3
            if stripe == 0:
                source[y, x] = [50, 100, 200]   # Blue
            elif stripe == 1:
                source[y, x] = [100, 200, 100]  # Green
            else:
                source[y, x] = [200, 80, 150]   # Pink

# =============================================================================
# STEP 2: Create the canvas for your 2x2 grid
# =============================================================================
# TODO: Calculate the canvas dimensions for a 2x2 grid
# Hint: The grid should be twice the height and twice the width of the source
grid_height = ???  # Replace ??? with the correct calculation
grid_width = ???   # Replace ??? with the correct calculation

canvas = np.zeros((grid_height, grid_width, 3), dtype=np.uint8)

# =============================================================================
# STEP 3: Place four color variations in the grid
# =============================================================================
# TODO: Fill in the channel orders for each quadrant
# Remember: [0, 1, 2] means [R, G, B] (original)
#           [1, 2, 0] rotates channels: R->G, G->B, B->R
#           [2, 0, 1] rotates the other way: R->B, G->R, B->G

# Top-left quadrant: Original colors
canvas[0:height, 0:width] = source[:, :, [0, 1, 2]]

# Top-right quadrant: First variation
# TODO: Choose a different channel order
canvas[0:height, width:grid_width] = source[:, :, [?, ?, ?]]

# Bottom-left quadrant: Second variation
# TODO: Choose another different channel order
canvas[height:grid_height, 0:width] = source[:, :, [?, ?, ?]]

# Bottom-right quadrant: Third variation
# TODO: Choose your final channel order
canvas[height:grid_height, width:grid_width] = source[:, :, [?, ?, ?]]

# =============================================================================
# STEP 4: Save your pop art creation
# =============================================================================
output = Image.fromarray(canvas, mode='RGB')
output.save('my_warhol.png')
print("Saved my_warhol.png - Your Warhol-style pop art!")
