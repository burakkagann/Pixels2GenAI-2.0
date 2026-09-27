import numpy as np
from PIL import Image

# Create square flag (Switzerland uses 1:1 ratio)
size = 300
flag = np.zeros((size, size, 3), dtype=np.uint8)

# TODO Step 1: Fill entire background with red
# Hint: Use flag[:, :] = [255, 0, 0]

# TODO Step 2: Create vertical bar of cross (centred, white)
# The bar width should be size // 5 (60 pixels)
# Calculate left and right positions to centre it
# Hint: left = (size - bar_width) // 2

# TODO Step 3: Create horizontal bar of cross (centred, white)
# Same proportions as vertical bar

# Save
result = Image.fromarray(flag, mode='RGB')
result.save('switzerland_flag.png')
