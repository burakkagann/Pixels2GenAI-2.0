import numpy as np
from PIL import Image

# Step 1: Set up canvas dimensions
size = 512
center = size // 2
canvas = np.zeros((size, size, 3), dtype=np.uint8)

# Step 2: Create coordinate grids for polar calculations
y_coords, x_coords = np.ogrid[:size, :size]
# Shift coordinates so origin is at center
x_centered = x_coords - center
y_centered = y_coords - center

# Step 3: Calculate polar coordinates (angle and radius from center)
angle = np.arctan2(y_centered, x_centered)  # Angle in radians (-pi to pi)
radius = np.sqrt(x_centered**2 + y_centered**2)  # Distance from center

# Step 4: Create a procedural source pattern (colorful gradient based on angle and radius)
# Map angle to hue-like values and radius to brightness
red_channel = ((np.sin(angle * 3 + radius * 0.05) + 1) * 127).astype(np.uint8)
green_channel = ((np.cos(angle * 2 + radius * 0.03) + 1) * 127).astype(np.uint8)
blue_channel = ((np.sin(radius * 0.08) + 1) * 127).astype(np.uint8)

source_pattern = np.stack([red_channel, green_channel, blue_channel], axis=-1)

# Step 5: Define kaleidoscope parameters
num_folds = 6  # 6-fold symmetry (classic kaleidoscope)
wedge_angle = 2 * np.pi / num_folds  # Angle of each wedge (60 degrees)

# Step 6: Create the kaleidoscope effect
# Normalize angle to be positive (0 to 2*pi)
angle_positive = angle + np.pi

# Map all angles into a single wedge, then mirror every other segment
wedge_index = (angle_positive / wedge_angle).astype(int)
angle_in_wedge = angle_positive - wedge_index * wedge_angle

# Mirror odd-numbered wedges to create reflection symmetry
is_odd_wedge = wedge_index % 2 == 1
angle_mirrored = np.where(is_odd_wedge, wedge_angle - angle_in_wedge, angle_in_wedge)

# Step 7: Sample from the source pattern using the mirrored angle
# Convert mirrored polar coordinates back to Cartesian
x_sampled = (radius * np.cos(angle_mirrored - np.pi)).astype(int) + center
y_sampled = (radius * np.sin(angle_mirrored - np.pi)).astype(int) + center

# Clip to valid indices
x_sampled = np.clip(x_sampled, 0, size - 1)
y_sampled = np.clip(y_sampled, 0, size - 1)

# Step 8: Create the kaleidoscope image by sampling
canvas = source_pattern[y_sampled, x_sampled]

# Step 9: Apply circular mask for clean edges
mask = radius <= center - 10
canvas = np.where(mask[:, :, np.newaxis], canvas, 0)

# Step 10: Save the result
output_image = Image.fromarray(canvas, mode='RGB')
output_image.save('simple_kaleidoscope.png')
