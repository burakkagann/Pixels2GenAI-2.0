import numpy as np
from PIL import Image

# Step 1: Create image dimensions and coordinate grids
height, width = 512, 512
center_x, center_y = width // 2, height // 2

# Create coordinate arrays centered on the image
y_coords, x_coords = np.ogrid[:height, :width]
dx = center_x - x_coords  # Vector pointing toward center (x component)
dy = center_y - y_coords  # Vector pointing toward center (y component)

# Step 2: Calculate angle of each vector using arctan2
# arctan2 returns angle in radians from -pi to pi
angle = np.arctan2(dy, dx)

# Step 3: Map angle to hue (0-255 range for full color spectrum)
# Convert from [-pi, pi] to [0, 1] then to [0, 255]
hue = ((angle + np.pi) / (2 * np.pi) * 255).astype(np.uint8)

# Step 4: Create RGB image using HSV-to-RGB conversion
# For simplicity, we map hue directly to RGB using a color wheel approach
image = np.zeros((height, width, 3), dtype=np.uint8)

# Map hue to RGB using segment-based color wheel
# Divide the 0-255 range into 6 segments for ROYGBV colors
segment = hue // 43  # 0-5 (approximately 6 segments)
remainder = (hue % 43) * 6  # 0-255 within segment

image[:, :, 0] = np.where(segment == 0, 255,
                 np.where(segment == 1, 255 - remainder,
                 np.where(segment == 2, 0,
                 np.where(segment == 3, 0,
                 np.where(segment == 4, remainder, 255)))))

image[:, :, 1] = np.where(segment == 0, remainder,
                 np.where(segment == 1, 255,
                 np.where(segment == 2, 255,
                 np.where(segment == 3, 255 - remainder,
                 np.where(segment == 4, 0, 0)))))

image[:, :, 2] = np.where(segment == 0, 0,
                 np.where(segment == 1, 0,
                 np.where(segment == 2, remainder,
                 np.where(segment == 3, 255,
                 np.where(segment == 4, 255, 255 - remainder)))))

# Step 5: Save the result
output_image = Image.fromarray(image, mode='RGB')
output_image.save('simple_vector_field.png')
