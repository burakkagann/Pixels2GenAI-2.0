import numpy as np
from PIL import Image

# Create blank canvas (standard 2:3 flag ratio)
height, width = 300, 450
flag = np.zeros((height, width, 3), dtype=np.uint8)

# Blue stripe (left third: columns 0-149)
flag[:, 0:150, 0] = 0    # Red channel
flag[:, 0:150, 1] = 85   # Green channel
flag[:, 0:150, 2] = 164  # Blue channel

# White stripe (middle third: columns 150-299)
flag[:, 150:300, :] = 255

# Red stripe (right third: columns 300-449)
flag[:, 300:450, 0] = 239
flag[:, 300:450, 1] = 65
flag[:, 300:450, 2] = 53

# Save the flag
result = Image.fromarray(flag, mode='RGB')
result.save('france_flag.png')
