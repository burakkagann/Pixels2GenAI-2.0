import numpy as np
from PIL import Image
import os

# =============================================================================
# Step 1: Load the Brandenburg Gate image
# =============================================================================
# The image is stored in the same folder as this script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, 'bbtor.jpg')

# Load image and convert to grayscale
# Grayscale has one channel, simplifying the convolution process
img = Image.open(IMAGE_PATH).convert('L')

# Resize for faster processing (256x171 is manageable for nested loops)
img = img.resize((256, 171))

# Convert to numpy array with float64 for precision
# Float64 prevents overflow when computing kernel products
image = np.array(img, dtype=np.float64)
print(f"Loaded Brandenburg Gate image: {image.shape[1]}x{image.shape[0]} pixels")

# =============================================================================
# Step 2: Define the edge detection kernel
# =============================================================================
# Laplacian kernel: detects edges by computing second derivative
# Positive center (8) surrounded by negative neighbors (-1 each)
# Sum of weights = 0, so uniform regions produce zero output
edge_kernel = np.array([
    [-1, -1, -1],
    [-1,  8, -1],
    [-1, -1, -1]
], dtype=np.float64)

print("\nEdge detection kernel (Laplacian):")
print(edge_kernel)

# =============================================================================
# Step 3: The Complete Convolution Function
# =============================================================================
def apply_convolution(image, kernel):
    """
    Apply a convolution kernel to a grayscale image.

    The algorithm:
    1. Pad the image to handle border pixels
    2. For each pixel position (y, x):
       a. Extract the region under the kernel
       b. Multiply region by kernel (element-wise)
       c. Sum all values to get the output pixel

    This follows the convolution formula: C_i = Σ_j{I_{i+k-j} W_j}
    as documented in SciPy ndimage.convolve.

    Parameters:
        image (np.ndarray): 2D array of pixel values (grayscale)
        kernel (np.ndarray): 2D array of kernel weights (e.g., 3x3)

    Returns:
        np.ndarray: Convolved image (same size as input)
    """
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2

    # Create output array (same size as input)
    height, width = image.shape
    output = np.zeros((height, width), dtype=np.float64)

    # Pad the image to handle borders
    # 'edge' mode repeats the edge pixels outward, avoiding black borders
    padded = np.pad(image, pad, mode='edge')

    # ==========================================================================
    # The core convolution loop - THIS IS THE KEY PART!
    # ==========================================================================
    for y in range(height):
        for x in range(width):
            # Extract the region that the kernel covers
            # Because we padded, we can safely access y:y+kernel_size
            region = padded[y:y + kernel_size, x:x + kernel_size]

            # Element-wise multiplication and sum
            # This IS convolution - multiply corresponding elements, then sum
            output[y, x] = np.sum(region * kernel)

    return output

# =============================================================================
# Step 4: Apply the convolution
# =============================================================================
print("\nApplying convolution (this may take a moment)...")
result = apply_convolution(image, edge_kernel)
print("Convolution complete!")

# =============================================================================
# Step 5: Post-process output values
# =============================================================================
# Edge detection kernels sum to 0, so the convolution output can include:
#   - Negative values (where center pixel is darker than neighbors)
#   - Values > 255 (where center pixel is much brighter than neighbors)
#
# Two approaches (see Core Concept 2 in README.rst):
#   Option 1: np.clip(result, 0, 255) -- simple, discards negative edges
#   Option 2: Min-max normalization -- preserves all edge responses
#
# We use Option 2 here for richer visualization.

# Option 1: Clip to valid range (simple but may lose information)
result_clipped = np.clip(result, 0, 255)

# Option 2: Normalize to 0-255 (preserves relative intensities)
result_min = result.min()
result_max = result.max()
if result_max > result_min:
    result_normalized = 255 * (result - result_min) / (result_max - result_min)
else:
    result_normalized = result_clipped

# Use normalized version for better visualization of all edges
final_result = result_normalized.astype(np.uint8)

# Save the edge detection result
output_image = Image.fromarray(final_result, mode='L')
output_image.save(os.path.join(SCRIPT_DIR, 'visuals', 'convolution_solution.png'))

print(f"\nResult saved as convolution_solution.png")
print(f"  Original pixel range: 0-255")
print(f"  After convolution: {result.min():.1f} to {result.max():.1f}")
print(f"  (Normalized back to 0-255 for display)")
print()
print("The edges of the Brandenburg Gate should now be clearly visible!")

# =============================================================================
# Step 6: Create a side-by-side comparison
# =============================================================================
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(10, 4), dpi=150)

# Left panel: Original image
axes[0].imshow(image, cmap='gray', vmin=0, vmax=255)
axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
axes[0].axis('off')

# Right panel: Edge detection result
axes[1].imshow(final_result, cmap='gray', vmin=0, vmax=255)
axes[1].set_title('Edge Detection Result', fontsize=12, fontweight='bold')
axes[1].axis('off')

plt.suptitle('Convolution in Action: Finding Edges',
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, 'visuals', 'convolution_comparison.png'), dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Comparison saved as convolution_comparison.png")
