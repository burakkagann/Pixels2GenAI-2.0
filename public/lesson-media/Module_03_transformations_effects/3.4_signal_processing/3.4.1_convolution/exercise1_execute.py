import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

# =============================================================================
# Step 1: Load the Brandenburg Gate image
# =============================================================================
# The image is stored in the same folder as this script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, 'bbtor.jpg')

# Load image and convert to grayscale for single-channel convolution
img = Image.open(IMAGE_PATH).convert('L')

# Resize for faster processing while keeping recognizable detail
img = img.resize((400, 267))

# np.array() converts a PIL image into a NumPy array (a grid of numbers).
# dtype=np.float64 uses 64-bit floats so multiplication won't overflow.
canvas = np.array(img, dtype=np.float64)
print(f"Loaded Brandenburg Gate image: {canvas.shape[1]}x{canvas.shape[0]} pixels")

# =============================================================================
# Step 2: Define four kernels with different effects
# =============================================================================
# Each kernel is a small grid of weights. When the kernel slides over the
# image, it computes a weighted sum of the pixels underneath it.

kernels = {
    'Original': None,  # No convolution -- shows the input as-is

    # Blur (Box Filter): all weights equal, averages the 3x3 neighborhood.
    # np.ones((3, 3)) creates a 3x3 array filled with 1s.
    # Dividing by 9 normalizes so brightness is preserved.
    'Blur (Box)': np.ones((3, 3), dtype=np.float64) / 9.0,

    # Sharpen: center weight > 1, cross-neighbors negative.
    # This amplifies the center pixel relative to its surroundings.
    'Sharpen': np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
    ], dtype=np.float64),

    # Edge Detection (Laplacian): positive center, all neighbors negative.
    # Uniform regions cancel to zero; boundaries become bright.
    'Edge Detect': np.array([
        [-1, -1, -1],
        [-1,  8, -1],
        [-1, -1, -1]
    ], dtype=np.float64)
}

# =============================================================================
# Step 3: Convolution function
# =============================================================================
def apply_convolution(image, kernel):
    """Apply a convolution kernel to a grayscale image."""
    if kernel is None:
        return image.copy()

    kernel_size = kernel.shape[0]
    pad = kernel_size // 2

    # np.zeros_like() creates a same-shape array filled with zeros.
    output = np.zeros_like(image)

    # np.pad() adds extra rows/columns around the image so the kernel can
    # process edge pixels without going out of bounds.
    # mode='edge' repeats the outermost pixel values outward.
    padded = np.pad(image, pad, mode='edge')

    height, width = image.shape

    # Slide the kernel over every pixel
    for y in range(height):
        for x in range(width):
            # Extract the region the kernel covers
            region = padded[y:y + kernel_size, x:x + kernel_size]

            # np.sum(region * kernel) multiplies each pixel by its kernel
            # weight, then adds everything up to produce one output pixel.
            output[y, x] = np.sum(region * kernel)

    return output

# =============================================================================
# Step 4: Apply each kernel and build comparison grid
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=150)
axes = axes.flatten()

for idx, (name, kernel) in enumerate(kernels.items()):
    result = apply_convolution(canvas, kernel)

    # np.clip() limits values to the range [0, 255].
    # Edge detection can produce negatives and values > 255.
    result = np.clip(result, 0, 255)

    axes[idx].imshow(result, cmap='gray', vmin=0, vmax=255)
    axes[idx].set_title(name, fontsize=14, fontweight='bold', pad=10)
    axes[idx].axis('off')

    # Overlay kernel values in the corner
    if kernel is not None:
        kernel_text = '\n'.join([' '.join([f'{v:5.1f}' for v in row])
                                  for row in kernel])
        axes[idx].text(0.02, 0.02, f'Kernel:\n{kernel_text}',
                      transform=axes[idx].transAxes,
                      fontsize=7, fontfamily='monospace',
                      verticalalignment='bottom',
                      bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.suptitle('Different Kernels Produce Different Effects',
             fontsize=16, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, 'visuals', 'exercise1_result.png'), dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Saved exercise1_result.png")
