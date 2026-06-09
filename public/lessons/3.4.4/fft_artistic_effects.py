import numpy as np
from PIL import Image

def create_artistic_pattern(size=200):
    """Create a visually interesting pattern for effect demonstration."""
    image = np.zeros((size, size), dtype=np.float64)

    # Radial gradient background
    center = size // 2
    for y in range(size):
        for x in range(size):
            dist = np.sqrt((x - center)**2 + (y - center)**2)
            image[y, x] = max(0, 255 - dist * 2)

    # Add some geometric shapes for edge content
    # Star pattern
    for angle in range(0, 360, 45):
        rad = np.radians(angle)
        for r in range(20, 80, 2):
            x = int(center + r * np.cos(rad))
            y = int(center + r * np.sin(rad))
            if 0 <= x < size and 0 <= y < size:
                image[y, x] = 255
                # Make lines thicker
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < size and 0 <= ny < size:
                            image[ny, nx] = 255

    return image

def create_mask(size, mask_type, params=None):
    """Create various frequency domain masks."""
    mask = np.zeros((size, size), dtype=np.float64)
    center = size // 2

    y_coords, x_coords = np.ogrid[:size, :size]
    distances = np.sqrt((x_coords - center)**2 + (y_coords - center)**2)

    if mask_type == 'low_pass':
        radius = params.get('radius', 30)
        mask[distances <= radius] = 1.0

    elif mask_type == 'high_pass':
        radius = params.get('radius', 20)
        mask[distances > radius] = 1.0

    elif mask_type == 'band_pass':
        inner = params.get('inner', 15)
        outer = params.get('outer', 50)
        mask[(distances > inner) & (distances <= outer)] = 1.0

    elif mask_type == 'notch':
        # Remove specific frequencies (creates interesting patterns)
        mask = np.ones((size, size), dtype=np.float64)
        # Cut out horizontal and vertical bands
        band_width = params.get('width', 5)
        mask[center-band_width:center+band_width, :] = 0.3
        mask[:, center-band_width:center+band_width] = 0.3

    return mask

def apply_filter(image, mask):
    """Apply frequency filter and return normalized result."""
    fft = np.fft.fftshift(np.fft.fft2(image))
    filtered = fft * mask
    result = np.abs(np.fft.ifft2(np.fft.ifftshift(filtered)))

    # Normalize to 0-255
    result_min, result_max = result.min(), result.max()
    if result_max > result_min:
        return ((result - result_min) / (result_max - result_min) * 255).astype(np.uint8)
    return np.zeros_like(result, dtype=np.uint8)

# Create source image
size = 200
original = create_artistic_pattern(size)

# Apply different filters
effects = [
    ('Original', original.astype(np.uint8)),
    ('Blur (Low-Pass)', apply_filter(original, create_mask(size, 'low_pass', {'radius': 25}))),
    ('Edges (High-Pass)', apply_filter(original, create_mask(size, 'high_pass', {'radius': 15}))),
    ('Band-Pass', apply_filter(original, create_mask(size, 'band_pass', {'inner': 10, 'outer': 40}))),
]

# Create 2x2 grid
gap = 4
grid_size = size * 2 + gap
grid = np.ones((grid_size, grid_size), dtype=np.uint8) * 200

# Place images
positions = [(0, 0), (0, size + gap), (size + gap, 0), (size + gap, size + gap)]
for (name, img), (row, col) in zip(effects, positions):
    grid[row:row+size, col:col+size] = img

# Save result
result = Image.fromarray(grid, mode='L')
result.save('frequency_effects_comparison.png')

print("Artistic frequency effects comparison complete!")
print(f"Output saved as 'frequency_effects_comparison.png'")
print(f"\n2x2 Grid layout:")
print("  Top-left:     Original pattern")
print("  Top-right:    Blur effect (low-pass, radius=25)")
print("  Bottom-left:  Edge enhancement (high-pass, radius=15)")
print("  Bottom-right: Band-pass (inner=10, outer=40)")
