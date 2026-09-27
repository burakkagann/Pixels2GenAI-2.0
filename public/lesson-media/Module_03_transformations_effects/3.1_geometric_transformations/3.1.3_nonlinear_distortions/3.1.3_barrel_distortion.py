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

# Step 2: Apply barrel distortion
center_y, center_x = size // 2, size // 2
strength = 0.5  # Distortion strength (0 = none, 1 = strong)
distorted = np.zeros_like(image)

for y in range(size):
    for x in range(size):
        # Convert to normalized coordinates centered at image center
        dy = (y - center_y) / center_y
        dx = (x - center_x) / center_x

        # Calculate radius from center
        radius = np.sqrt(dx**2 + dy**2)

        # Apply barrel distortion formula
        if radius > 0:
            factor = 1 + strength * radius**2
            source_dx = dx / factor
            source_dy = dy / factor
        else:
            source_dx, source_dy = 0, 0

        # Convert back to pixel coordinates
        source_x = int(source_dx * center_x + center_x)
        source_y = int(source_dy * center_y + center_y)

        # Clip to valid range and copy pixel
        source_x = np.clip(source_x, 0, size - 1)
        source_y = np.clip(source_y, 0, size - 1)
        distorted[y, x] = image[source_y, source_x]

# Step 3: Save the result
result = Image.fromarray(distorted)
result.save('barrel_distortion_output.png')
