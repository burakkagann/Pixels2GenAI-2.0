import numpy as np
from scipy import ndimage
from PIL import Image

# ============================================
# CONFIGURATION - Modify these parameters
# ============================================
canvas_size = 400
rotation_angle = 30  # Try different angles: 45, 90, 135, etc.
background_color = [30, 30, 50]  # Dark blue background [R, G, B]
shape_color = [255, 150, 50]    # Orange shape [R, G, B]

# ============================================
# Step 1: Create canvas with background color
# ============================================
# TODO: Create a canvas array filled with the background_color
# Hint: Use np.zeros() then assign the background color
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
# Your code here: fill canvas with background_color

# ============================================
# Step 2: Create a shape to rotate
# ============================================
# TODO: Draw a shape on a separate transparent layer
# Create a shape array for the object to rotate
shape_layer = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# TODO: Draw a rectangle or other shape using array slicing
# Example: shape_layer[top:bottom, left:right] = shape_color
# Your code here:

# ============================================
# Step 3: Rotate the shape
# ============================================
# TODO: Use ndimage.rotate() to rotate the shape
# Hint: rotated = ndimage.rotate(shape_layer, angle, reshape=False, mode='constant', cval=0)
# Your code here:

# ============================================
# Step 4: Combine shape with background
# ============================================
# TODO: Overlay the rotated shape onto the canvas
# Hint: Where the rotated shape is not black, use its color
# Your code here:

# ============================================
# Step 5: Save the result
# ============================================
output = Image.fromarray(canvas, mode='RGB')
output.save('my_rotation.png')
