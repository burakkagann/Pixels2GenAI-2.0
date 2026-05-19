
import numpy as np
from PIL import Image

# Step 1: Create a colorful gradient image (no external file needed)
height, width = 200, 200
image = np.zeros((height, width, 3), dtype=np.uint8)

# Create a radial gradient with multiple colors
for y in range(height):
    for x in range(width):
        # Distance from center creates circular pattern
        cx, cy = width // 2, height // 2
        distance = np.sqrt((x - cx)**2 + (y - cy)**2)

        # Create colorful bands based on distance
        image[y, x, 0] = int(128 + 127 * np.sin(distance * 0.1))  # Red
        image[y, x, 1] = int(128 + 127 * np.sin(distance * 0.1 + 2))  # Green
        image[y, x, 2] = int(128 + 127 * np.sin(distance * 0.1 + 4))  # Blue

# Step 2: Create a 2x2 canvas for the Warhol grid
canvas_height = height * 2
canvas_width = width * 2
canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

# Step 3: Place four color variations by rotating channels
# Original [R, G, B] arrangement
canvas[0:height, 0:width] = image[:, :, [0, 1, 2]]

# Rotate to [G, B, R] - shifts colors dramatically
canvas[0:height, width:] = image[:, :, [1, 2, 0]]

# Rotate to [B, R, G] - another distinct variation
canvas[height:, 0:width] = image[:, :, [2, 0, 1]]

# Swap to [R, B, G] - subtle but noticeable change
canvas[height:, width:] = image[:, :, [0, 2, 1]]

# Step 4: Save the result
output = Image.fromarray(canvas, mode='RGB')
output.save('simple_warhol.png')
print("Saved simple_warhol.png - A 2x2 Warhol-style pop art grid!")
