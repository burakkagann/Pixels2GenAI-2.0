import numpy as np
from PIL import Image

# Image setup (already done for you)
height, width = 512, 512
center_x, center_y = width // 2, height // 2

# Create coordinate grids (already done for you)
y_coords, x_coords = np.ogrid[:height, :width]
rel_x = x_coords - center_x
rel_y = y_coords - center_y

# Calculate distance from center (already done for you)
distance = np.sqrt(rel_x**2 + rel_y**2)
distance[distance == 0] = 1  # Avoid division by zero at center

# TODO 1: Calculate the rotational component (circular flow)
# Hint: For rotation, swap x and y and negate one: (-rel_y, rel_x)
dx_rotation = 0  # Replace with correct formula
dy_rotation = 0  # Replace with correct formula

# TODO 2: Calculate the radial inward component (pull toward center)
# Hint: Normalize by dividing by distance to get unit vectors
dx_radial = 0  # Replace with correct formula
dy_radial = 0  # Replace with correct formula

# TODO 3: Combine rotation and radial components
# Hint: Add them together with appropriate weights
# Try: 70% rotation + 30% radial for a nice spiral effect
dx_combined = 0  # Combine dx_rotation and dx_radial
dy_combined = 0  # Combine dy_rotation and dy_radial

# Calculate angle from combined vector (already done for you)
angle = np.arctan2(dy_combined, dx_combined)

# Color mapping function (already done for you)
def angle_to_rgb(angle):
    """Convert angle to RGB color using color wheel."""
    hue = ((angle + np.pi) / (2 * np.pi) * 255).astype(np.uint8)
    image = np.zeros((*hue.shape, 3), dtype=np.uint8)
    segment = hue // 43
    remainder = (hue % 43) * 6

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
    return image

# Generate and save image (already done for you)
image = angle_to_rgb(angle)
output = Image.fromarray(image, mode='RGB')
output.save('vortex_field.png')
