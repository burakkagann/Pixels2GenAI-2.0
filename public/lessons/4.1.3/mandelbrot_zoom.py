import numpy as np
from PIL import Image

def generate_mandelbrot(center_x, center_y, zoom_level, width=512, height=512,
                        max_iterations=200):
    """
    Generate a Mandelbrot set image centered at a specific point.

    Parameters:
    -----------
    center_x : float
        Real component of the center point
    center_y : float
        Imaginary component of the center point
    zoom_level : float
        Zoom factor (higher = more zoomed in)
    width, height : int
        Image dimensions in pixels
    max_iterations : int
        Maximum iterations before assuming point is in the set

    Returns:
    --------
    np.ndarray : RGB image array
    """
    # Calculate viewing window based on center and zoom
    # Base range is 3.5 units wide, 3.0 units tall
    x_range = 3.5 / zoom_level
    y_range = 3.0 / zoom_level

    x_min = center_x - x_range / 2
    x_max = center_x + x_range / 2
    y_min = center_y - y_range / 2
    y_max = center_y + y_range / 2

    # Create complex grid
    real_values = np.linspace(x_min, x_max, width)
    imaginary_values = np.linspace(y_min, y_max, height)
    real_grid, imaginary_grid = np.meshgrid(real_values, imaginary_values)
    c = real_grid + 1j * imaginary_grid

    # Initialize iteration arrays
    z = np.zeros_like(c, dtype=np.complex128)
    iteration_count = np.zeros(c.shape, dtype=np.int32)

    # Iterate the Mandelbrot formula
    for i in range(max_iterations):
        still_bounded = np.abs(z) <= 2
        z[still_bounded] = z[still_bounded] ** 2 + c[still_bounded]
        iteration_count[still_bounded] += 1

    # Apply colorful gradient (using HSV-like mapping)
    image_array = np.zeros((height, width, 3), dtype=np.uint8)

    mask_in_set = iteration_count == max_iterations
    mask_outside = ~mask_in_set

    # Create vibrant color mapping for points outside the set
    # Map iteration count to hue-like color
    normalized = iteration_count[mask_outside] / max_iterations

    # Color scheme: purple -> blue -> cyan -> green -> yellow -> red
    # Using sine waves to create smooth color transitions
    image_array[mask_outside, 0] = (128 + 127 * np.sin(normalized * 3 * np.pi)).astype(np.uint8)
    image_array[mask_outside, 1] = (128 + 127 * np.sin(normalized * 3 * np.pi + 2)).astype(np.uint8)
    image_array[mask_outside, 2] = (128 + 127 * np.sin(normalized * 3 * np.pi + 4)).astype(np.uint8)

    # Points in the set remain black
    image_array[mask_in_set] = [0, 0, 0]

    return image_array

# =============================================================================
# Generate zoomed view into the "Seahorse Valley"
# =============================================================================
# This region shows beautiful spiral structures

# Seahorse Valley coordinates (a famous region of the Mandelbrot set)
seahorse_center_x = -0.745
seahorse_center_y = 0.113
zoom = 50  # 50x zoom

print("Generating zoomed Mandelbrot view...")
print(f"Center: ({seahorse_center_x}, {seahorse_center_y})")
print(f"Zoom level: {zoom}x")

# Generate with higher iterations for more detail at this zoom level
zoomed_image = generate_mandelbrot(
    center_x=seahorse_center_x,
    center_y=seahorse_center_y,
    zoom_level=zoom,
    max_iterations=300  # More iterations reveal more detail when zoomed
)

# Save the zoomed image
output = Image.fromarray(zoomed_image, mode='RGB')
output.save('mandelbrot_zoomed.png')
print("Zoomed Mandelbrot saved as 'mandelbrot_zoomed.png'")
print("\nNotice how the spiral structures at this zoom level look similar")
print("to patterns in the full set - this is fractal self-similarity!")
