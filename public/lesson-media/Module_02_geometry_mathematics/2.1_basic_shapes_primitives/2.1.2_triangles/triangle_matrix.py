
import numpy as np
from PIL import Image

# Step 1: Create a column vector of values 0 to 399
# reshape(400, 1) turns the 1D array into a 2D column vector
x = np.arange(400).reshape(400, 1)

# Step 2: Create the distance matrix using transpose
# x has shape (400, 1), x.T has shape (1, 400)
# NumPy broadcasts to create a (400, 400) matrix where element [i,j] = i + j
distance_matrix = x + x.T

# Step 3: Apply conditional masking to create triangle
# Points where i + j <= 400 form a triangle in the upper-left corner
# This creates a diagonal boundary line from (0, 400) to (400, 0)
threshold = 400
triangle_mask = distance_matrix <= threshold

# Step 4: Create the image
# Convert boolean mask to uint8 (True->255, False->0)
canvas = np.zeros((400, 400), dtype=np.uint8)
canvas[triangle_mask] = 255

# Save result
Image.fromarray(canvas).save('triangle_matrix.png')

