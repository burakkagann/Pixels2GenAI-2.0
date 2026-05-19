import numpy as np
from PIL import Image

# Step 1: Create a 400x400 coordinate grid
# linspace creates evenly spaced values from -10 to 10
dim = np.linspace(-10, 10, 400)
# meshgrid creates 2D coordinate arrays from 1D arrays
# The [1] adds a third dimension for broadcasting with multiple hills
x, y, _ = np.meshgrid(dim, dim, [1])

# Step 2: Define positions and widths of three "hills"
# Each hill is a Gaussian centered at (position_x, position_y)
position_x = np.array([-3.0, 7.0, 9.0])     # x-coordinates of hill centers
position_y = np.array([0.0, 8.0, -9.0])     # y-coordinates of hill centers
width_x = np.array([5.3, 8.3, 4.0])         # spread in x direction
width_y = np.array([6.3, 5.7, 4.0])         # spread in y direction

# Step 3: Calculate height as a combination of Gaussians
# This formula computes distance from each hill center, scaled by width
d = np.sqrt(((x - position_x) / width_x) ** 2 + ((y - position_y) / width_y) ** 2)
z = np.exp(-d ** 2)  # Gaussian function: high at center, falls off with distance
# Shape is (400, 400, 3) because we have 3 hills

# Step 4: Combine hills into a single landscape
z = z.sum(axis=2)   # Sum all hills to get a single height map
# Normalize height values to range (0.0 to 1.0)
znorm = (z - z.min()) / (z.max() - z.min())

# Step 5: Create stepped contour visualization
# Multiply by 8 to get 8 levels, then scale to visible grayscale (0-255)
n_levels = 8
contour = (znorm * n_levels).astype(np.uint8) * 32
im = Image.fromarray(contour, mode='L')
im.save('contour_steps.png')
print("Saved contour_steps.png - stepped contour with 8 levels")

# Step 6: Create isoline visualization
# Use modulo to find where height crosses specific thresholds
# (znorm * 100).round() gives 100 discrete height values
# % 16 == 0 finds every 16th level, creating thin contour lines
isolines = ((znorm * 100).round() % 16) == 0
isolines = (isolines * 255).astype(np.uint8)
im = Image.fromarray(isolines, mode='L')
im.save('contour_isolines.png')
print("Saved contour_isolines.png - isoline visualization")

print("\nDone! Two contour visualizations created.")
print("  - contour_steps.png: Stepped bands (like elevation colors on a map)")
print("  - contour_isolines.png: Thin lines (like topographic map contours)")
