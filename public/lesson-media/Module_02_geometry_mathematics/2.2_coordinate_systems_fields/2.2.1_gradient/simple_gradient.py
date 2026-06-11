
import numpy as np
from PIL import Image

# Step 1: Define image dimensions (rectangular to show gradient direction)
height = 300
width = 800

# Step 2: Create a 1D array of evenly spaced values from 0 (black) to 255 (white)
# np.linspace(start, stop, num) generates 'num' values between start and stop
gradient_values = np.linspace(0, 255, width, dtype=np.uint8)

# Step 3: Create the full 2D grayscale image by repeating the gradient for each row
# Broadcasting: a 1D array of shape (width,) becomes (height, width)
gradient_image = np.tile(gradient_values, (height, 1))

# Step 4: Save the gradient image
output = Image.fromarray(gradient_image, mode='L')  # 'L' mode for grayscale
output.save('simple_gradient.png')

