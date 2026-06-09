import numpy as np
from PIL import Image

# Step 1: Create a colorful checkerboard pattern
size = 400
tile_size = 50
image = np.zeros((size, size, 3), dtype=np.uint8)

colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
for row in range(size // tile_size):
    for col in range(size // tile_size):
        color = colors[(row + col) % len(colors)]
        y_start, y_end = row * tile_size, (row + 1) * tile_size
        x_start, x_end = col * tile_size, (col + 1) * tile_size
        image[y_start:y_end, x_start:x_end] = color

# Step 2: Apply swirl distortion
center_y, center_x = size // 2, size // 2
max_radius = size // 2
twist_amount = 2.0  # Number of full rotations at the edge
distorted = np.zeros_like(image)

for y in range(size):
    for x in range(size):
        # Calculate distance and angle from center
        dy = y - center_y
        dx = x - center_x
        radius = np.sqrt(dx**2 + dy**2)
        angle = np.arctan2(dy, dx)

        # Calculate twist angle based on radius (more twist toward center)
        twist = twist_amount * np.pi * (1 - radius / max_radius)

        # Calculate source coordinates
        source_x = int(center_x + radius * np.cos(angle - twist))
        source_y = int(center_y + radius * np.sin(angle - twist))

        # Clip to valid range and copy pixel
        source_x = np.clip(source_x, 0, size - 1)
        source_y = np.clip(source_y, 0, size - 1)
        distorted[y, x] = image[source_y, source_x]

# Step 3: Save the result
result = Image.fromarray(distorted)
result.save('swirl_distortion_output.png')
