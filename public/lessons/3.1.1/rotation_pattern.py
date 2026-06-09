import numpy as np
from scipy import ndimage
from PIL import Image

# Step 1: Create canvas and define parameters
canvas_size = 500
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Define rotation parameters
number_of_rotations = 18
angle_step = 180 / number_of_rotations  # Spread across 180 degrees

# Step 2: Create a simple colored rectangle shape
# The rectangle is offset from center to create the fan effect
shape = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Draw a cyan rectangle (positioned to one side)
rect_top, rect_bottom = 200, 300      # Vertical position (centered)
rect_left, rect_right = 250, 450       # Horizontal position (right side)
shape[rect_top:rect_bottom, rect_left:rect_right] = [0, 180, 220]  # Cyan color

# Step 3: Apply multiple rotations and accumulate
for i in range(number_of_rotations):
    rotation_angle = i * angle_step

    # Rotate the shape
    rotated_shape = ndimage.rotate(shape, rotation_angle, reshape=False, mode='constant', cval=0)

    # Add to canvas with additive blending (clipped to 255)
    # Reduce intensity so overlaps don't saturate immediately
    intensity_factor = 0.4
    contribution = (rotated_shape * intensity_factor).astype(np.uint8)
    canvas = np.clip(canvas.astype(np.int16) + contribution.astype(np.int16), 0, 255).astype(np.uint8)

# Step 4: Save the artistic result
output = Image.fromarray(canvas, mode='RGB')
output.save('rotation_pattern.png')