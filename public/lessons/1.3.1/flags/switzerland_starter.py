import numpy as np
from PIL import Image

# Create square flag (Switzerland uses 1:1 ratio)
size = 300
flag = np.zeros((size, size, 3), dtype=np.uint8)

# TODO Step 1: Fill entire background with red
# Hint: Use flag[:, :] = [255, 0, 0]
# Your code here

# TODO Step 2: Create vertical bar of cross (centered, white)
# The bar width should be size // 5
# Calculate left and right positions to center it
# Hint: left = (size - bar_width) // 2, right = left + bar_width
# Your code here

# TODO Step 3: Create horizontal bar of cross (centered, white)
# Same proportions as vertical bar
# Hint: Similar calculation for top and bottom positions
# Your code here

# Save the result
result = Image.fromarray(flag, mode='RGB')
result.save('switzerland_flag.png')

