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

# Step 2: Apply combined horizontal AND vertical wave distortions
h_amplitude = 15  # Horizontal wave amplitude
h_frequency = 3   # Horizontal wave frequency
v_amplitude = 15  # Vertical wave amplitude
v_frequency = 4   # Vertical wave frequency

distorted = np.zeros_like(image)

for y in range(size):
    for x in range(size):
        # Horizontal wave: shifts x based on y position
        h_offset = int(h_amplitude * np.sin(2 * np.pi * h_frequency * y / size))
        # Vertical wave: shifts y based on x position
        v_offset = int(v_amplitude * np.sin(2 * np.pi * v_frequency * x / size))

        # Calculate source coordinates with both offsets
        source_x = (x + h_offset) % size
        source_y = (y + v_offset) % size

        distorted[y, x] = image[source_y, source_x]

# Step 3: Save the result
result = Image.fromarray(distorted)
result.save('combined_waves_output.png')
