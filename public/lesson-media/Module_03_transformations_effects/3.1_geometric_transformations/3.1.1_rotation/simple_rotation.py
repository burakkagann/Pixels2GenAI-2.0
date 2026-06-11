import numpy as np
from scipy import ndimage
from PIL import Image

# Step 1: Create a simple colored rectangle on a dark background
canvas_size = 400
image = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Draw a cyan rectangle in the center
rect_top, rect_bottom = 150, 250
rect_left, rect_right = 100, 300
image[rect_top:rect_bottom, rect_left:rect_right] = [0, 200, 200]  # Cyan color

# Step 2: Rotate the image by 45 degrees
rotation_angle = 45
rotated_image = ndimage.rotate(image, rotation_angle, reshape=False, mode='constant', cval=0)

# Step 3: Create side-by-side comparison (original and rotated)
comparison = np.zeros((canvas_size, canvas_size * 2 + 20, 3), dtype=np.uint8)
comparison[:, :canvas_size] = image                    # Left: original
comparison[:, canvas_size + 20:] = rotated_image       # Right: rotated (with gap)

# Step 4: Save the result
output = Image.fromarray(comparison, mode='RGB')
output.save('simple_rotation.png')