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
# Create a canvas array and fill it with the background color
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
canvas[:, :] = background_color  # Fill entire canvas with background

# ============================================
# Step 2: Create a shape to rotate
# ============================================
# Create a separate layer for the shape (on black background for easy masking)
shape_layer = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Draw a rectangle in the center-right area
# This offset position will show rotation clearly
rect_top = 150
rect_bottom = 250
rect_left = 180
rect_right = 350

shape_layer[rect_top:rect_bottom, rect_left:rect_right] = shape_color

# ============================================
# Step 3: Rotate the shape
# ============================================
# Use scipy.ndimage.rotate() to rotate the shape layer
# reshape=False keeps the output size the same as input
# mode='constant' fills empty areas with cval (0 = black)
rotated_shape = ndimage.rotate(
    shape_layer,
    rotation_angle,
    reshape=False,
    mode='constant',
    cval=0
)

# ============================================
# Step 4: Combine shape with background
# ============================================
# Create a mask: where the rotated shape is not black (has color)
# We check if any channel has value > 0
mask = np.any(rotated_shape > 0, axis=2)

# Apply the rotated shape to canvas where mask is True
# This preserves the background where the shape is transparent (black)
canvas[mask] = rotated_shape[mask]

# ============================================
# Step 5: Save the result
# ============================================
output = Image.fromarray(canvas, mode='RGB')
output.save('rotation_solution.png')

