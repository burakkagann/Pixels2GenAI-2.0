

import numpy as np
from PIL import Image

# Configuration
CANVAS_SIZE = 512
NUM_STARS = 400
BACKGROUND = 0

# Create a black canvas
canvas = np.full((CANVAS_SIZE, CANVAS_SIZE), BACKGROUND, dtype=np.uint8)

# Step 1: Generate random star positions (uniform distribution)
x_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)
y_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)

# Step 2: Generate random brightness values for each star
# Range from dim (50) to bright (255) simulating distance
brightness = np.random.randint(50, 256, size=NUM_STARS)

# Step 3: Sort stars by brightness (dim first, bright last)
# This ensures brighter stars are drawn on top of dimmer ones
# if they happen to overlap at the same pixel
sort_indices = np.argsort(brightness)
x_coords = x_coords[sort_indices]
y_coords = y_coords[sort_indices]
brightness = brightness[sort_indices]

# Step 4: Place stars with varying brightness
# We loop because each star has a different brightness value
# (Alternative: use np.put or advanced indexing with unique positions)
for x, y, b in zip(x_coords, y_coords, brightness):
    canvas[y, x] = b

# Bonus: Add a few very bright "foreground" stars (larger, 3x3 pixels)
num_bright_stars = 10
x_bright = np.random.randint(2, CANVAS_SIZE - 2, size=num_bright_stars)
y_bright = np.random.randint(2, CANVAS_SIZE - 2, size=num_bright_stars)

for x, y in zip(x_bright, y_bright):
    # Create a small 3x3 cross pattern for bright stars
    canvas[y, x] = 255          # Center
    canvas[y - 1, x] = 200      # Top
    canvas[y + 1, x] = 200      # Bottom
    canvas[y, x - 1] = 200      # Left
    canvas[y, x + 1] = 200      # Right

# Save the result
image = Image.fromarray(canvas, mode='L')
image.save('brightness_variation.png')
