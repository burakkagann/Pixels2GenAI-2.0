import numpy as np
from PIL import Image

# Step 1: Create a colorful checkerboard pattern (400x400)
size = 400
tile_size = 50
image = np.zeros((size, size, 3), dtype=np.uint8)

# Fill with alternating colored tiles
colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
for row in range(size // tile_size):
    for col in range(size // tile_size):
        color = colors[(row + col) % len(colors)]
        y_start, y_end = row * tile_size, (row + 1) * tile_size
        x_start, x_end = col * tile_size, (col + 1) * tile_size
        image[y_start:y_end, x_start:x_end] = color

# Step 2: Apply horizontal wave distortion
amplitude = 20  # How far pixels shift
frequency = 3   # Number of wave cycles
distorted = np.zeros_like(image)

for y in range(size):
    for x in range(size):
        # Calculate new x coordinate with sine wave offset
        offset = int(amplitude * np.sin(2 * np.pi * frequency * y / size))
        source_x = (x + offset) % size  # Wrap around edges
        distorted[y, x] = image[y, source_x]

# Step 3: Save the result
result = Image.fromarray(distorted)
result.save('wave_distortion_output.png')
