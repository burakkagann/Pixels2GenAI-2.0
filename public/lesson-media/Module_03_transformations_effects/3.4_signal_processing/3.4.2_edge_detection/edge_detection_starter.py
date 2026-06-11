import numpy as np
from PIL import Image

# Step 1: Create a custom test image (256x256 grayscale)
height, width = 256, 256
image = np.zeros((height, width), dtype=np.float64)

# TODO: Create your own pattern! Ideas:
# - Diagonal stripes
# - Concentric squares
# - A simple letter shape
# - Checkerboard pattern
#
# Example: Draw a simple "T" shape
# image[50:70, 80:180] = 255   # Horizontal bar
# image[60:180, 115:145] = 255  # Vertical bar

# YOUR PATTERN CODE HERE:
# ...

# Step 2: Define the Sobel kernels
# TODO: Define the Sobel Gx kernel (detects vertical edges)
# Hint: The kernel has values [-1, 0, 1] in each row, weighted by [1, 2, 1]
sobel_gx = np.array([
    # TODO: Fill in the 3x3 Gx kernel
])

# TODO: Define the Sobel Gy kernel (detects horizontal edges)
# Hint: Gy is the transpose of Gx
sobel_gy = np.array([
    # TODO: Fill in the 3x3 Gy kernel
])

# Step 3: Apply Sobel operator using convolution
edge_magnitude = np.zeros((height, width), dtype=np.float64)

for y in range(1, height - 1):
    for x in range(1, width - 1):
        # TODO: Extract the 3x3 neighborhood around pixel (y, x)
        neighborhood = None  # Replace with correct slice

        # TODO: Compute horizontal gradient (Gx)
        gradient_x = 0  # Replace with correct calculation

        # TODO: Compute vertical gradient (Gy)
        gradient_y = 0  # Replace with correct calculation

        # TODO: Compute edge magnitude using Euclidean distance
        edge_magnitude[y, x] = 0  # Replace with correct formula

# Step 4: Normalize to 0-255 and save
if edge_magnitude.max() > 0:
    edge_normalized = (255 * edge_magnitude / edge_magnitude.max()).astype(np.uint8)
else:
    edge_normalized = edge_magnitude.astype(np.uint8)

output_image = Image.fromarray(edge_normalized, mode='L')
output_image.save('my_edge_detection.png')

print("Edge detection complete!")
print(f"Output saved as: my_edge_detection.png")
print(f"Maximum edge strength: {edge_magnitude.max():.2f}")

# CHALLENGE EXTENSION:
# Try implementing the Prewitt operator instead of Sobel.
# Prewitt uses unweighted kernels:
#   Prewitt Gx: [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
#   Prewitt Gy: [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
# Compare the results with your Sobel implementation!
