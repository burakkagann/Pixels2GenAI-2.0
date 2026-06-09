import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Step 1: Create a test image with both horizontal and vertical features
height, width = 200, 200
image = np.zeros((height, width), dtype=np.float64)

# Vertical stripes (will be detected by Gx)
image[:, 40:60] = 255
image[:, 100:120] = 255
image[:, 160:180] = 255

# Horizontal stripes (will be detected by Gy)
image[20:40, :] = 200
image[80:100, :] = 200
image[140:160, :] = 200

# Step 2: Define Sobel kernels
sobel_gx = np.array([[-1, 0, 1],
                     [-2, 0, 2],
                     [-1, 0, 1]])

sobel_gy = np.array([[-1, -2, -1],
                     [ 0,  0,  0],
                     [ 1,  2,  1]])

# Step 3: Apply convolution for each kernel
gx_result = np.zeros((height, width), dtype=np.float64)
gy_result = np.zeros((height, width), dtype=np.float64)

for y in range(1, height - 1):
    for x in range(1, width - 1):
        neighborhood = image[y-1:y+2, x-1:x+2]
        gx_result[y, x] = np.sum(sobel_gx * neighborhood)
        gy_result[y, x] = np.sum(sobel_gy * neighborhood)

# Step 4: Compute combined magnitude
combined = np.sqrt(gx_result**2 + gy_result**2)

# Normalize all results to 0-255
def normalize(arr):
    if arr.max() > 0:
        return (255 * np.abs(arr) / np.abs(arr).max()).astype(np.uint8)
    return arr.astype(np.uint8)

gx_normalized = normalize(gx_result)
gy_normalized = normalize(gy_result)
combined_normalized = normalize(combined)

# Step 5: Create comparison figure
fig, axes = plt.subplots(2, 2, figsize=(10, 10))

# Original image
axes[0, 0].imshow(image, cmap='gray')
axes[0, 0].set_title('Original Image\n(Horizontal & Vertical Stripes)', fontsize=12, fontweight='bold')
axes[0, 0].axis('off')

# Gx result (detects vertical edges)
axes[0, 1].imshow(gx_normalized, cmap='gray')
axes[0, 1].set_title('Gx Result\n(Vertical Edges Only)', fontsize=12, fontweight='bold')
axes[0, 1].axis('off')

# Gy result (detects horizontal edges)
axes[1, 0].imshow(gy_normalized, cmap='gray')
axes[1, 0].set_title('Gy Result\n(Horizontal Edges Only)', fontsize=12, fontweight='bold')
axes[1, 0].axis('off')

# Combined magnitude
axes[1, 1].imshow(combined_normalized, cmap='gray')
axes[1, 1].set_title('Combined Magnitude\n(All Edges)', fontsize=12, fontweight='bold')
axes[1, 1].axis('off')

plt.suptitle('Sobel Edge Detection: Directional Comparison', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('gradient_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Gradient comparison created!")
print("Output saved as: gradient_comparison.png")
print(f"Gx max value: {np.abs(gx_result).max():.2f} (vertical edges)")
print(f"Gy max value: {np.abs(gy_result).max():.2f} (horizontal edges)")
print(f"Combined max: {combined.max():.2f}")
