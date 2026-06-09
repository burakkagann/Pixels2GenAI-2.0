import numpy as np
from PIL import Image

# Step 1: Create a test image with geometric shapes (256x256 grayscale)
height, width = 256, 256
image = np.zeros((height, width), dtype=np.float64)

# Draw a white rectangle in the center
image[80:180, 60:120] = 255

# Draw a white circle on the right side
center_y, center_x, radius = 128, 180, 40
y_coords, x_coords = np.ogrid[:height, :width]
circle_mask = (x_coords - center_x)**2 + (y_coords - center_y)**2 <= radius**2
image[circle_mask] = 255

# Step 2: Define the Sobel kernels for edge detection
# Gx detects vertical edges (changes in horizontal direction)
sobel_gx = np.array([[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]])

# Gy detects horizontal edges (changes in vertical direction)
sobel_gy = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]])

# Step 3: Apply Sobel operator using convolution (nested loops for clarity)
edge_magnitude = np.zeros((height, width), dtype=np.float64)

for y in range(1, height - 1):
    for x in range(1, width - 1):
        # Extract 3x3 neighborhood around current pixel
        neighborhood = image[y-1:y+2, x-1:x+2]

        # Compute horizontal gradient (Gx)
        gradient_x = np.sum(sobel_gx * neighborhood)

        # Compute vertical gradient (Gy)
        gradient_y = np.sum(sobel_gy * neighborhood)

        # Compute edge magnitude using Euclidean distance
        edge_magnitude[y, x] = np.sqrt(gradient_x**2 + gradient_y**2)

# Step 4: Normalize to 0-255 range and save
edge_normalized = (255 * edge_magnitude / edge_magnitude.max()).astype(np.uint8)
output_image = Image.fromarray(edge_normalized, mode='L')
output_image.save('edge_detection_output.png')

print("Edge detection complete!")
print(f"Output saved as: edge_detection_output.png")
print(f"Image size: {width}x{height} pixels")
print(f"Maximum edge strength: {edge_magnitude.max():.2f}")
