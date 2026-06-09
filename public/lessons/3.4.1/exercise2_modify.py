import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# =============================================================================
# Step 1: Load the Brandenburg Gate image
# =============================================================================
# The image is stored in the same folder as this script.
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bbtor.jpg')

img = Image.open(IMAGE_PATH).convert('L')
img = img.resize((400, 267))

# np.array() converts a PIL image into a NumPy array (a grid of numbers).
# dtype=np.float64 uses 64-bit floats for precision during multiplication.
canvas = np.array(img, dtype=np.float64)
print(f"Loaded Brandenburg Gate image: {canvas.shape[1]}x{canvas.shape[0]} pixels")

# =============================================================================
# MODIFY the kernel values below to achieve each goal
# =============================================================================
# This is the IDENTITY kernel: center = 1, everything else = 0.
# The output is identical to the input (each pixel maps to itself).
#
# np.array() creates a 2D array from nested lists.
# dtype=np.float64 ensures decimal values (like 1/9) are stored precisely.

kernel = np.array([
    [0, 0, 0],
    [0, 1, 0],       # <-- CHANGE THESE VALUES
    [0, 0, 0]        #     to achieve each goal
], dtype=np.float64)
# =============================================================================

# =============================================================================
# Step 2: Convolution function (DO NOT MODIFY)
# =============================================================================
def apply_convolution(image, kernel):
    """Apply a convolution kernel to a grayscale image."""
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2

    # np.zeros_like() creates a same-shape, same-type array of zeros.
    output = np.zeros_like(image)

    # np.pad() adds extra rows/columns around the image borders.
    # mode='edge' copies the outermost pixels outward so the kernel
    # always has valid neighbors, even at image edges.
    padded = np.pad(image, pad, mode='edge')

    height, width = image.shape

    for y in range(height):
        for x in range(width):
            region = padded[y:y + kernel_size, x:x + kernel_size]
            # np.sum() adds up all elements in the array.
            # region * kernel multiplies each pixel by its kernel weight.
            output[y, x] = np.sum(region * kernel)

    return output

# =============================================================================
# Step 3: Apply convolution and display result (DO NOT MODIFY)
# =============================================================================
print(f"\nKernel being applied:")
print(kernel)
print(f"Kernel sum: {np.sum(kernel):.2f}")

result = apply_convolution(canvas, kernel)

# np.clip() restricts values to the range [0, 255].
# Without clipping, edge detection values can go negative or above 255.
result_display = np.clip(result, 0, 255)

# Create side-by-side comparison
fig, axes = plt.subplots(1, 2, figsize=(10, 4), dpi=150)

axes[0].imshow(canvas, cmap='gray', vmin=0, vmax=255)
axes[0].set_title('Original', fontsize=14, fontweight='bold')
axes[0].axis('off')

axes[1].imshow(result_display, cmap='gray', vmin=0, vmax=255)
axes[1].set_title('After Convolution', fontsize=14, fontweight='bold')
axes[1].axis('off')

# Show kernel values as text overlay
kernel_text = '\n'.join([' '.join([f'{v:6.2f}' for v in row]) for row in kernel])
axes[1].text(0.02, 0.02, f'Kernel:\n{kernel_text}',
            transform=axes[1].transAxes,
            fontsize=8, fontfamily='monospace',
            verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.suptitle('Convolution Result', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('exercise2_result.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Saved exercise2_result.png")
