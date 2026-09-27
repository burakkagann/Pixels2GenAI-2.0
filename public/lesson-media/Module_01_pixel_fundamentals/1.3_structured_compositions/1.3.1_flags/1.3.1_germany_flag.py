import numpy as np
from PIL import Image

# Create blank canvas
height, width = 300, 450
flag = np.zeros((height, width, 3), dtype=np.uint8)

# Black stripe (top third: rows 0-99)
flag[0:100, :, :] = [0, 0, 0]

# Red stripe (middle third: rows 100-199)
flag[100:200, :, :] = [221, 0, 0]

# Gold stripe (bottom third: rows 200-299)
flag[200:300, :, :] = [255, 206, 0]

# Save the flag
result = Image.fromarray(flag, mode='RGB')
result.save('germany_flag.png')
