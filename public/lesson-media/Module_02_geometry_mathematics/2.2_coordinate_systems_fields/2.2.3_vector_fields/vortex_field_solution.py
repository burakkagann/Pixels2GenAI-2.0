import numpy as np
from PIL import Image

# Step 1: Image setup
height, width = 512, 512
center_x, center_y = width // 2, height // 2

# Step 2: Create coordinate grids
y_coords, x_coords = np.ogrid[:height, :width]
rel_x = x_coords - center_x  # Distance from center in x
rel_y = y_coords - center_y  # Distance from center in y

# Step 3: Calculate distance from center
distance = np.sqrt(rel_x**2 + rel_y**2)
distance[distance == 0] = 1  # Avoid division by zero at center

# Step 4: Calculate the rotational component (circular flow)
# For counterclockwise rotation: (-y, x)
# The vectors are perpendicular to the radial direction
dx_rotation = -rel_y
dy_rotation = rel_x

# Step 5: Calculate the radial inward component
# Normalize to get unit vectors pointing toward center
dx_radial = -rel_x / distance  # Negative for inward
dy_radial = -rel_y / distance

# Step 6: Combine rotation and radial with weights
# 70% rotation gives strong swirl, 30% radial adds inward pull
rotation_weight = 0.7
radial_weight = 0.3

dx_combined = rotation_weight * dx_rotation + radial_weight * dx_radial * distance
dy_combined = rotation_weight * dy_rotation + radial_weight * dy_radial * distance

# Step 7: Calculate angle from combined vector
angle = np.arctan2(dy_combined, dx_combined)

# Step 8: Map angle to RGB color
def angle_to_rgb(angle):
    """Convert angle (radians) to RGB color using color wheel."""
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

# Step 9: Generate and save image
image = angle_to_rgb(angle)
output = Image.fromarray(image, mode='RGB')
output.save('vortex_field.png')

