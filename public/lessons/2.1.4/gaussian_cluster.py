
import numpy as np
from PIL import Image

# Configuration
CANVAS_SIZE = 400       # Width and height in pixels
NUM_STARS = 200         # Number of stars in the cluster
BACKGROUND = 0          # Black background

# Cluster parameters
CENTER_X = 200          # Cluster center X coordinate
CENTER_Y = 200          # Cluster center Y coordinate
SPREAD = 60             # Standard deviation (controls cluster tightness)

# Step 1: Create a black canvas
canvas = np.full((CANVAS_SIZE, CANVAS_SIZE), BACKGROUND, dtype=np.uint8)

# Step 2: Generate Gaussian-distributed coordinates
# np.random.normal(mean, std_dev, size) creates a bell-curve distribution
x_coords = np.random.normal(CENTER_X, SPREAD, size=NUM_STARS)
y_coords = np.random.normal(CENTER_Y, SPREAD, size=NUM_STARS)

# Step 3: Clip coordinates to stay within canvas bounds
# Without clipping, some stars would be outside the visible area
x_coords = np.clip(x_coords, 0, CANVAS_SIZE - 1).astype(int)
y_coords = np.clip(y_coords, 0, CANVAS_SIZE - 1).astype(int)

# Step 4: Place stars using integer array indexing
canvas[y_coords, x_coords] = 255

# Step 5: Save the result
image = Image.fromarray(canvas, mode='L')
image.save('gaussian_cluster.png')
