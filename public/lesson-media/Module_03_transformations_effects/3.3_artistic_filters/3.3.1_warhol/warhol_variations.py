"""
Warhol Variations - Exercise 1 Demo

Creates a 2x3 grid showing all six RGB channel permutations applied to
a colorful source image. This demonstrates the full range of pop art
color effects achievable through channel manipulation.

Framework: F1 (Hands-On Discovery)
Concepts: Channel permutation effects, comparative visualization
"""

import numpy as np
from PIL import Image

# Create a visually interesting source image
height, width = 150, 150
source = np.zeros((height, width, 3), dtype=np.uint8)

# Create concentric circles with different colors
cx, cy = width // 2, height // 2
for y in range(height):
    for x in range(width):
        # Distance from center
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)

        # Create colorful concentric rings
        ring = int(dist / 15) % 5
        if ring == 0:
            source[y, x] = [255, 100, 50]   # Orange-red
        elif ring == 1:
            source[y, x] = [50, 200, 100]   # Green
        elif ring == 2:
            source[y, x] = [100, 50, 200]   # Purple
        elif ring == 3:
            source[y, x] = [200, 200, 50]   # Yellow
        else:
            source[y, x] = [50, 150, 200]   # Sky blue

# Define all 6 channel permutations with descriptive labels
permutations = [
    ([0, 1, 2], "Original"),
    ([0, 2, 1], "Swap G-B"),
    ([1, 0, 2], "Swap R-G"),
    ([1, 2, 0], "Rotate Left"),
    ([2, 0, 1], "Rotate Right"),
    ([2, 1, 0], "Swap R-B"),
]

# Create a 2x3 grid canvas
gap = 10
cols = 3
rows = 2
canvas_width = cols * width + (cols - 1) * gap
canvas_height = rows * height + (rows - 1) * gap

canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 30  # Dark background

# Place each variation in the grid
for idx, (perm, label) in enumerate(permutations):
    row = idx // cols
    col = idx % cols

    x_start = col * (width + gap)
    y_start = row * (height + gap)

    # Apply the channel permutation
    variation = source[:, :, perm]

    # Place on canvas
    canvas[y_start:y_start + height, x_start:x_start + width] = variation

# Save the result
output = Image.fromarray(canvas, mode='RGB')
output.save('warhol_variations.png')
print("Saved warhol_variations.png - Grid showing all 6 channel permutations!")
print("\nPermutation effects shown:")
for perm, label in permutations:
    print(f"  {label}: channels = {perm}")
