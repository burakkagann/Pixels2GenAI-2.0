

import numpy as np
from PIL import Image

# Step 1: Create blank canvas (standard 2:3 flag ratio)
height, width = 300, 450
flag = np.zeros((height, width, 3), dtype=np.uint8)

# Step 2: Create three vertical bands using column slicing
# Blue stripe (left third: columns 0-149)
flag[:, 0:150, 0] = 0    # Red channel
flag[:, 0:150, 1] = 85   # Green channel
flag[:, 0:150, 2] = 164  # Blue channel (French blue #0055A4)

# White stripe (middle third: columns 150-299)
flag[:, 150:300, :] = 255  # All channels set to 255 for white

# Red stripe (right third: columns 300-449)
flag[:, 300:450, 0] = 239  # Red channel (French red #EF4135)
flag[:, 300:450, 1] = 65   # Green channel
flag[:, 300:450, 2] = 53   # Blue channel

# Step 3: Save the flag
result = Image.fromarray(flag, mode='RGB')
result.save('france_flag.png')
