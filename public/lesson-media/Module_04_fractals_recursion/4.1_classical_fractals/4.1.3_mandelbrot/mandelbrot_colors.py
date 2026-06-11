import numpy as np
from PIL import Image

def compute_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iterations):
    """
    Compute the Mandelbrot set iteration counts.

    Returns a 2D array where each value represents how many iterations
    the point took to escape (or max_iterations if it never escaped).
    """
    # Create complex grid
    real_values = np.linspace(x_min, x_max, width)
    imaginary_values = np.linspace(y_min, y_max, height)
    real_grid, imaginary_grid = np.meshgrid(real_values, imaginary_values)
    c = real_grid + 1j * imaginary_grid

    # Initialize
    z = np.zeros_like(c, dtype=np.complex128)
    iteration_count = np.zeros(c.shape, dtype=np.int32)

    # Iterate
    for i in range(max_iterations):
        still_bounded = np.abs(z) <= 2
        z[still_bounded] = z[still_bounded] ** 2 + c[still_bounded]
        iteration_count[still_bounded] += 1

    return iteration_count

def apply_grayscale(iteration_count, max_iterations):
    """Simple grayscale mapping: white outside, black inside the set."""
    normalized = iteration_count / max_iterations
    gray = (normalized * 255).astype(np.uint8)

    # Points in the set (max iterations) should be black
    gray[iteration_count == max_iterations] = 0

    # Create RGB from grayscale
    image = np.stack([gray, gray, gray], axis=-1)
    return image

def apply_fire_colormap(iteration_count, max_iterations):
    """Fire colormap: black -> red -> orange -> yellow -> white."""
    height, width = iteration_count.shape
    image = np.zeros((height, width, 3), dtype=np.uint8)

    normalized = iteration_count / max_iterations
    mask_outside = iteration_count < max_iterations

    # Fire gradient: increase red first, then add green, then blue
    r = np.minimum(normalized * 3, 1.0) * 255
    g = np.maximum(0, np.minimum((normalized - 0.33) * 3, 1.0)) * 255
    b = np.maximum(0, (normalized - 0.67) * 3) * 255

    image[mask_outside, 0] = r[mask_outside].astype(np.uint8)
    image[mask_outside, 1] = g[mask_outside].astype(np.uint8)
    image[mask_outside, 2] = b[mask_outside].astype(np.uint8)

    # Inside the set: black
    image[~mask_outside] = [0, 0, 0]
    return image

def apply_ocean_colormap(iteration_count, max_iterations):
    """Ocean colormap: deep blue -> cyan -> light blue."""
    height, width = iteration_count.shape
    image = np.zeros((height, width, 3), dtype=np.uint8)

    normalized = iteration_count / max_iterations
    mask_outside = iteration_count < max_iterations

    # Ocean gradient: blue stays high, green increases, red low
    r = (normalized * 100).astype(np.uint8)
    g = (normalized * 200 + 55).astype(np.uint8)
    b = (200 + normalized * 55).astype(np.uint8)

    image[mask_outside, 0] = r[mask_outside]
    image[mask_outside, 1] = g[mask_outside]
    image[mask_outside, 2] = b[mask_outside]

    # Inside the set: dark blue
    image[~mask_outside] = [10, 20, 60]
    return image

def apply_rainbow_colormap(iteration_count, max_iterations):
    """Cyclic rainbow colormap using sine waves for smooth transitions."""
    height, width = iteration_count.shape
    image = np.zeros((height, width, 3), dtype=np.uint8)

    normalized = iteration_count / max_iterations
    mask_outside = iteration_count < max_iterations

    # Use sine waves with phase offsets to create rainbow effect
    # Multiply by a higher frequency for more color bands
    freq = 5 * np.pi  # Number of color cycles

    r = (128 + 127 * np.sin(normalized * freq)).astype(np.uint8)
    g = (128 + 127 * np.sin(normalized * freq + 2 * np.pi / 3)).astype(np.uint8)
    b = (128 + 127 * np.sin(normalized * freq + 4 * np.pi / 3)).astype(np.uint8)

    image[mask_outside, 0] = r[mask_outside]
    image[mask_outside, 1] = g[mask_outside]
    image[mask_outside, 2] = b[mask_outside]

    # Inside the set: black
    image[~mask_outside] = [0, 0, 0]
    return image

# =============================================================================
# Generate color comparison grid
# =============================================================================

print("Computing Mandelbrot set iteration counts...")

# Parameters for all images
width, height = 400, 400
x_min, x_max = -2.2, 0.8
y_min, y_max = -1.5, 1.5
max_iterations = 100

# Compute iteration counts once (this is the slow part)
iteration_count = compute_mandelbrot(
    width, height, x_min, x_max, y_min, y_max, max_iterations
)

print("Applying different color mappings...")

# Apply each colormap
grayscale = apply_grayscale(iteration_count, max_iterations)
fire = apply_fire_colormap(iteration_count, max_iterations)
ocean = apply_ocean_colormap(iteration_count, max_iterations)
rainbow = apply_rainbow_colormap(iteration_count, max_iterations)

# Create 2x2 grid with labels
# Add padding and labels
padding = 40  # Space for labels
grid_width = width * 2 + padding * 3
grid_height = height * 2 + padding * 3

# Create white background
comparison_grid = np.ones((grid_height, grid_width, 3), dtype=np.uint8) * 255

# Place images in grid
# Top-left: Grayscale
comparison_grid[padding:padding + height, padding:padding + width] = grayscale

# Top-right: Fire
comparison_grid[padding:padding + height, padding * 2 + width:padding * 2 + width * 2] = fire

# Bottom-left: Ocean
comparison_grid[padding * 2 + height:padding * 2 + height * 2, padding:padding + width] = ocean

# Bottom-right: Rainbow
comparison_grid[padding * 2 + height:padding * 2 + height * 2, padding * 2 + width:padding * 2 + width * 2] = rainbow

# Save the comparison grid
output = Image.fromarray(comparison_grid, mode='RGB')
output.save('mandelbrot_colors.png')
print("Color comparison saved as 'mandelbrot_colors.png'")
print("\nGrid layout:")
print("  Top-left: Grayscale    |  Top-right: Fire")
print("  Bottom-left: Ocean     |  Bottom-right: Rainbow")
print("\nNotice: Same mathematical data, completely different visual impact!")
