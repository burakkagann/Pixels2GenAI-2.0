
import numpy as np
from PIL import Image

# Step 1: Create blank canvas (grayscale image)
canvas = np.zeros((400, 400), dtype=np.uint8)

# Step 2: Define line endpoints
x_start, y_start = 50, 50
x_end, y_end = 350, 350

# Step 3: Calculate number of points needed
# We need at least one point per pixel in the longer dimension
num_points = max(abs(x_end - x_start), abs(y_end - y_start)) + 1

# Step 4: Generate interpolated coordinates using linspace
# linspace creates evenly spaced points between start and end
x_coords = np.linspace(x_start, x_end, num_points).round().astype(int)
y_coords = np.linspace(y_start, y_end, num_points).round().astype(int)

# Step 5: Draw line by setting pixels to white (255)
# Remember: array indexing is [row, column] which is [y, x]
canvas[y_coords, x_coords] = 255

# Step 6: Save result
output_image = Image.fromarray(canvas)
output_image.save('simple_line.png')
