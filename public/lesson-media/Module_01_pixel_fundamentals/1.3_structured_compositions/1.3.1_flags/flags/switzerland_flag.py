import numpy as np
from PIL import Image

# Step 1: Create square flag (Switzerland uses 1:1 ratio)
size = 300
flag = np.zeros((size, size, 3), dtype=np.uint8)

# Step 2: Fill entire background with red
flag[:, :] = [255, 0, 0]  # Swiss red

# Step 3: Create white vertical bar (centered)
# Bar width is 1/5 of total size
bar_width = size // 5  # 60 pixels
left = (size - bar_width) // 2  # 120
right = left + bar_width  # 180
flag[:, left:right, :] = 255  # White vertical bar

# Step 4: Create white horizontal bar (centered)
# Bar height is 1/5 of total size
bar_height = size // 5  # 60 pixels
top = (size - bar_height) // 2  # 120
bottom = top + bar_height  # 180
flag[top:bottom, :, :] = 255  # White horizontal bar

# Step 5: Save the flag
result = Image.fromarray(flag, mode='RGB')
result.save('switzerland_flag.png')
