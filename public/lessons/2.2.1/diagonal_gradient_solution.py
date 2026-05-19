
import numpy as np
from PIL import Image

# Step 1: Define image dimensions
size = 400

# Step 2: Create horizontal gradient values (0 to 255 across width)
# This creates a 1D array that will be broadcast across rows
horizontal = np.linspace(0, 255, size)

# Step 3: Create vertical gradient values (0 to 255 down height)
# reshape(-1, 1) creates a column vector for proper broadcasting
vertical = np.linspace(0, 255, size).reshape(-1, 1)

# Step 4: Combine horizontal and vertical components
# When we add these, broadcasting creates a 2D array where:
# - Each position (y, x) gets value: horizontal[x] + vertical[y]
# - Dividing by 2 averages them, creating smooth diagonal transition
diagonal = (horizontal + vertical) / 2

# Step 5: Convert to uint8 for image format (values 0-255)
gradient_image = diagonal.astype(np.uint8)

# Save the result
output = Image.fromarray(gradient_image, mode='L')
output.save('diagonal_gradient.png')

