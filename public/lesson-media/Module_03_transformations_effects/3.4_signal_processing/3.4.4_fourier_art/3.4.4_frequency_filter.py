import numpy as np
from PIL import Image

def create_test_pattern(size=256):
    """Create a pattern with both smooth regions and sharp edges."""
    image = np.zeros((size, size), dtype=np.float64)

    # Add smooth gradient background
    for y in range(size):
        for x in range(size):
            image[y, x] = (x / size) * 100

    # Add sharp geometric shapes
    # Rectangle
    image[50:100, 50:150] = 255
    # Circle
    center = (size * 3 // 4, size // 2)
    for y in range(size):
        for x in range(size):
            if (x - center[0])**2 + (y - center[1])**2 < 40**2:
                image[y, x] = 255

    # Add fine details (small squares)
    for i in range(4):
        for j in range(4):
            y_start = 180 + i * 18
            x_start = 30 + j * 18
            image[y_start:y_start+8, x_start:x_start+8] = 200

    return image

def create_circular_mask(size, radius, mask_type='low'):
    """Create a circular frequency mask."""
    mask = np.zeros((size, size), dtype=np.float64)
    center = size // 2

    y_coords, x_coords = np.ogrid[:size, :size]
    distances = np.sqrt((x_coords - center)**2 + (y_coords - center)**2)

    if mask_type == 'low':
        mask[distances <= radius] = 1.0
    else:  # high-pass
        mask[distances > radius] = 1.0

    return mask

def apply_frequency_filter(image, mask):
    """Apply a frequency domain filter to an image."""
    # Transform to frequency domain
    fft_result = np.fft.fft2(image)
    fft_shifted = np.fft.fftshift(fft_result)

    # Apply mask
    filtered = fft_shifted * mask

    # Transform back to spatial domain
    fft_unshifted = np.fft.ifftshift(filtered)
    reconstructed = np.fft.ifft2(fft_unshifted)

    return np.abs(reconstructed)

# Create test image
size = 256
original = create_test_pattern(size)

# Create filters with different radii
low_pass_mask = create_circular_mask(size, radius=30, mask_type='low')
high_pass_mask = create_circular_mask(size, radius=30, mask_type='high')

# Apply filters
low_pass_result = apply_frequency_filter(original, low_pass_mask)
high_pass_result = apply_frequency_filter(original, high_pass_mask)

# Normalize results to 0-255
def normalize_image(img):
    img_min, img_max = img.min(), img.max()
    if img_max > img_min:
        return ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    return np.zeros_like(img, dtype=np.uint8)

original_norm = normalize_image(original)
low_pass_norm = normalize_image(low_pass_result)
high_pass_norm = normalize_image(high_pass_result)

# Create 2x2 comparison grid
gap = 4
grid = np.ones((size * 2 + gap, size * 2 + gap), dtype=np.uint8) * 128

# Place images: Original (top-left), Low-pass mask (top-right),
#               Low-pass result (bottom-left), High-pass result (bottom-right)
grid[:size, :size] = original_norm
grid[:size, size+gap:] = (low_pass_mask * 255).astype(np.uint8)
grid[size+gap:, :size] = low_pass_norm
grid[size+gap:, size+gap:] = high_pass_norm

# Save result
result = Image.fromarray(grid, mode='L')
result.save('frequency_filter_comparison.png')

print("Frequency filtering comparison complete!")
print(f"Output saved as 'frequency_filter_comparison.png'")
print(f"\nGrid layout:")
print("  Top-left:     Original image")
print("  Top-right:    Low-pass mask (white = keep)")
print("  Bottom-left:  Low-pass result (smooth/blurred)")
print("  Bottom-right: High-pass result (edges only)")
print(f"\nFilter radius: 30 pixels (center of spectrum)")
