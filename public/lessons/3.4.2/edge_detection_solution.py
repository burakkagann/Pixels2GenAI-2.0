import numpy as np
from PIL import Image

# Step 1: Create a custom test image (256x256 grayscale)
height, width = 256, 256
image = np.zeros((height, width), dtype=np.float64)

# Draw a "T" shape pattern
# Horizontal bar of the T
image[50:70, 80:180] = 255
# Vertical bar of the T
image[60:180, 115:145] = 255

# Add a small square in the corner for variety
image[200:230, 200:230] = 200

# Step 2: Define the Sobel kernels
# Gx kernel detects vertical edges (changes in horizontal direction)
sobel_gx = np.array([[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]])

# Gy kernel detects horizontal edges (changes in vertical direction)
sobel_gy = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]])

# Step 3: Apply Sobel operator using convolution
edge_magnitude = np.zeros((height, width), dtype=np.float64)

for y in range(1, height - 1):
    for x in range(1, width - 1):
        # Extract the 3x3 neighborhood around pixel (y, x)
        neighborhood = image[y-1:y+2, x-1:x+2]

        # Compute horizontal gradient (Gx)
        gradient_x = np.sum(sobel_gx * neighborhood)

        # Compute vertical gradient (Gy)
        gradient_y = np.sum(sobel_gy * neighborhood)

        # Compute edge magnitude using Euclidean distance
        edge_magnitude[y, x] = np.sqrt(gradient_x**2 + gradient_y**2)

# Step 4: Normalize to 0-255 and save
if edge_magnitude.max() > 0:
    edge_normalized = (255 * edge_magnitude / edge_magnitude.max()).astype(np.uint8)
else:
    edge_normalized = edge_magnitude.astype(np.uint8)

output_image = Image.fromarray(edge_normalized, mode='L')
output_image.save('edge_detection_solution.png')

print("Edge detection complete!")
print(f"Output saved as: edge_detection_solution.png")
print(f"Image size: {width}x{height} pixels")
print(f"Maximum edge strength: {edge_magnitude.max():.2f}")

# How this solution works:
#
# 1. We create a "T" shape which has both horizontal and vertical edges,
#    making it a good test for the Sobel operator.
#
# 2. The Sobel Gx kernel [-1,0,1; -2,0,2; -1,0,1] computes the difference
#    between left and right neighbors, weighted by distance from center.
#    This detects vertical edges (where intensity changes horizontally).
#
# 3. The Sobel Gy kernel [-1,-2,-1; 0,0,0; 1,2,1] computes the difference
#    between top and bottom neighbors. This detects horizontal edges.
#
# 4. For each pixel, we slide the 3x3 kernels over it and compute:
#    - gradient_x: sum of element-wise multiplication with Gx kernel
#    - gradient_y: sum of element-wise multiplication with Gy kernel
#
# 5. The final edge magnitude combines both directions using the
#    Euclidean distance formula: sqrt(gx^2 + gy^2)
#
# 6. Normalization scales the result to 0-255 for display as an image.
