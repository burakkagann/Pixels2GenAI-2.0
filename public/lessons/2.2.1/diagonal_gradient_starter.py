
import numpy as np
from PIL import Image

# Step 1: Define image dimensions
size = 400

# Step 2: Create horizontal gradient values (0 to 255 across width)
# TODO: Use np.linspace() to create values from 0 to 255 with 'size' points
horizontal = None  # Replace with your code

# Step 3: Create vertical gradient values (0 to 255 down height)
# TODO: Use np.linspace() with reshape(-1, 1) to make it a column vector
vertical = None  # Replace with your code

# Step 4: Combine horizontal and vertical components
# TODO: Average the two components to create diagonal effect
# Hint: (horizontal + vertical) / 2
diagonal = None  # Replace with your code

# Step 5: Convert to uint8 and save
# TODO: Convert diagonal to uint8 dtype
gradient_image = None  # Replace with your code

# Save the result
output = Image.fromarray(gradient_image, mode='L')
output.save('my_diagonal_gradient.png')
