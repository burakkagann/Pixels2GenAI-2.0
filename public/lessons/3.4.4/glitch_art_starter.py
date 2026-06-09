import numpy as np
from PIL import Image

def create_source_image(size=256):
    """Create a synthetic image - DO NOT MODIFY."""
    image = np.zeros((size, size), dtype=np.float64)

    # Concentric squares
    for i in range(0, size // 2, 20):
        thickness = 3
        image[i:i+thickness, i:size-i] = 255
        image[size-i-thickness:size-i, i:size-i] = 255
        image[i:size-i, i:i+thickness] = 255
        image[i:size-i, size-i-thickness:size-i] = 255

    # Diagonal lines
    for offset in range(-size, size, 30):
        for i in range(size):
            x, y = i, i + offset
            if 0 <= y < size:
                image[y, x] = 200

    return image

# Create source image
size = 256
source = create_source_image(size)

# Transform to frequency domain (provided for you)
fft = np.fft.fft2(source)
fft_shifted = np.fft.fftshift(fft)
center = size // 2

# =====================================================
# TODO 1: Create an asymmetric glitch mask
# =====================================================
# The mask should have values between 0 and 1
# Try making the left half different from the right half
# Example: left side keeps low frequencies, right side keeps high frequencies

mask = np.ones((size, size), dtype=np.float64)  # Start with all ones

# YOUR CODE HERE: Modify the mask to create asymmetric filtering
# Hint: Use loops or numpy operations to set different values
# for the left half (x < center) vs right half (x >= center)
#
# Example structure:
# for y in range(size):
#     for x in range(size):
#         dist = np.sqrt((x - center)**2 + (y - center)**2)
#         if x < center:
#             mask[y, x] = ???  # Left side rule
#         else:
#             mask[y, x] = ???  # Right side rule

# =====================================================
# TODO 2: Add glitch holes (zeroed frequency regions)
# =====================================================
# Zero out random rectangular regions in the mask
# This creates "missing data" artifacts in the final image

# YOUR CODE HERE: Add at least 5 glitch holes
# Hint: Use np.random.randint() to pick random positions
# Then set mask[y_start:y_end, x_start:x_end] = 0
#
# Example:
# np.random.seed(42)  # For reproducibility
# for i in range(5):
#     gx = np.random.randint(0, size)
#     gy = np.random.randint(0, size)
#     hole_size = ???
#     mask[???:???, ???:???] = 0

# =====================================================
# Apply the glitch effect (provided for you)
# =====================================================
magnitude = np.abs(fft_shifted)
phase = np.angle(fft_shifted)

# Reconstruct with masked magnitude
glitched_fft = (magnitude * mask) * np.exp(1j * phase)
fft_unshifted = np.fft.ifftshift(glitched_fft)
result = np.abs(np.fft.ifft2(fft_unshifted))

# Normalize to 0-255
result_min, result_max = result.min(), result.max()
if result_max > result_min:
    result = (result - result_min) / (result_max - result_min) * 255
glitched = result.astype(np.uint8)

# Create side-by-side comparison
gap = 4
output = np.ones((size, size * 2 + gap), dtype=np.uint8) * 128
output[:, :size] = source.astype(np.uint8)
output[:, size + gap:] = glitched

# Save result
img = Image.fromarray(output, mode='L')
img.save('my_glitch_art.png')

print("Your glitch art has been created!")
print("Output saved as 'my_glitch_art.png'")
print("\nIf it looks the same as the original, you need to modify the mask!")
