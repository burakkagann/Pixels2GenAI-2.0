import numpy as np
from PIL import Image
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Configuration - Try changing these values!
# =============================================================================
CANVAS_SIZE = 256           # Size of the image (256x256 pixels)
SQUARE_SIZE = 32            # Size of each checkerboard square
KERNEL_SIZE = 5             # Size of the blur kernel (5x5)

# =============================================================================
# Step 1: Create a checkerboard pattern with sharp edges
# =============================================================================
# A checkerboard is ideal for demonstrating blur - the sharp black/white
# transitions become smooth gradients after convolution

canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.float64)

for row in range(CANVAS_SIZE):
    for col in range(CANVAS_SIZE):
        # Determine which square this pixel belongs to
        square_row = row // SQUARE_SIZE
        square_col = col // SQUARE_SIZE

        # Alternate between black (0) and white (255)
        if (square_row + square_col) % 2 == 0:
            canvas[row, col] = 255.0

# =============================================================================
# Step 2: Define a blur (averaging) kernel
# =============================================================================
# A blur kernel averages neighboring pixels together.
# Each value is 1/(kernel_size^2) so the total sums to 1.0
# This preserves the overall brightness of the image.

blur_kernel = np.ones((KERNEL_SIZE, KERNEL_SIZE), dtype=np.float64)
blur_kernel = blur_kernel / blur_kernel.sum()  # Normalize to sum to 1

print(f"Blur kernel ({KERNEL_SIZE}x{KERNEL_SIZE}):")
print(blur_kernel)
print()

# =============================================================================
# Step 3: Apply convolution manually
# =============================================================================
# Convolution slides the kernel over every pixel position, multiplies
# the kernel values by the underlying pixel values, and sums the result.

# Calculate output size (smaller due to border handling)
output_height = CANVAS_SIZE - KERNEL_SIZE + 1
output_width = CANVAS_SIZE - KERNEL_SIZE + 1
output = np.zeros((output_height, output_width), dtype=np.float64)

# Slide the kernel over the image
for y in range(output_height):
    for x in range(output_width):
        # Extract the region under the kernel
        region = canvas[y:y + KERNEL_SIZE, x:x + KERNEL_SIZE]

        # Element-wise multiply and sum (this IS convolution!)
        output[y, x] = np.sum(region * blur_kernel)

# =============================================================================
# Step 4: Create side-by-side comparison image
# =============================================================================
# Show original (left) and blurred (right) for easy comparison

# Crop original to match output size for fair comparison
original_cropped = canvas[KERNEL_SIZE//2:-(KERNEL_SIZE//2),
                          KERNEL_SIZE//2:-(KERNEL_SIZE//2)]

# Combine side by side with a small gap
gap = 10
combined_width = original_cropped.shape[1] + gap + output.shape[1]
combined = np.ones((output.shape[0], combined_width), dtype=np.float64) * 128

# Place original on left, blurred on right
combined[:, :original_cropped.shape[1]] = original_cropped
combined[:, original_cropped.shape[1] + gap:] = output

# Convert to 8-bit and save
result = Image.fromarray(combined.astype(np.uint8), mode='L')
result.save(os.path.join(SCRIPT_DIR, 'visuals', 'simple_convolution.png'))

print("Convolution complete!")
print(f"  Original size: {CANVAS_SIZE}x{CANVAS_SIZE}")
print(f"  Output size: {output_height}x{output_width}")
print(f"  (Output is smaller because we don't process border pixels)")
print()
print("Output saved as simple_convolution.png")
print("Left side: Original sharp checkerboard")
print("Right side: Blurred result after convolution")
