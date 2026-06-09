
import numpy as np
from PIL import Image

# Configuration
CANVAS_SIZE = 400       # Width and height in pixels
NUM_STARS = 150         # Number of stars to place
BACKGROUND = 0          # Black background (grayscale value)
STAR_BRIGHTNESS = 255   # White stars (grayscale value)

# Step 1: Create a black canvas (grayscale image)
canvas = np.full((CANVAS_SIZE, CANVAS_SIZE), BACKGROUND, dtype=np.uint8)

# Step 2: Generate random coordinates for star positions
# np.random.randint generates integers in range [low, high)
x_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)
y_coords = np.random.randint(0, CANVAS_SIZE, size=NUM_STARS)

# Step 3: Place stars using integer array indexing
# Note: NumPy uses [row, column] order, which is [y, x] in image coordinates
canvas[y_coords, x_coords] = STAR_BRIGHTNESS

# Step 4: Save the result
image = Image.fromarray(canvas, mode='L')  # 'L' for grayscale
image.save('simple_star.png')
