

import numpy as np
from PIL import Image

# Step 1: Create blank canvas (standard 2:3 flag ratio)
height, width = 300, 450
flag = np.zeros((height, width, 3), dtype=np.uint8)

# Step 2: Create three horizontal bands using row slicing
# Black stripe (top third: rows 0-99)
flag[0:100, :, :] = [0, 0, 0]  # Black

# Red stripe (middle third: rows 100-199)
flag[100:200, :, :] = [221, 0, 0]  # German red (#DD0000)

# Gold stripe (bottom third: rows 200-299)
flag[200:300, :, :] = [255, 206, 0]  # German gold (#FFCE00)

# Step 3: Save the flag
result = Image.fromarray(flag, mode='RGB')
result.save('germany_flag.png')

