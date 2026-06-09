import numpy as np
from PIL import Image

# =============================================================================
# PARAMETERS - Try changing these values!
# =============================================================================

# Image dimensions (pixels)
width = 512
height = 512

# Complex plane boundaries (the "viewing window")
# Default view shows the entire Mandelbrot set
x_min, x_max = -2.5, 1.0    # Real axis range
y_min, y_max = -1.5, 1.5    # Imaginary axis range

# Algorithm parameters
max_iterations = 100  # More iterations = more detail but slower

# =============================================================================
# STEP 1: Create the complex number grid
# =============================================================================
# Each pixel corresponds to a complex number c = x + iy
# We create a grid of complex numbers covering our viewing window

real_values = np.linspace(x_min, x_max, width)      # Real part (x-axis)
imaginary_values = np.linspace(y_min, y_max, height) # Imaginary part (y-axis)

# meshgrid creates 2D arrays from 1D arrays
# real_grid[i,j] = real_values[j], imag_grid[i,j] = imaginary_values[i]
real_grid, imaginary_grid = np.meshgrid(real_values, imaginary_values)

# Combine into complex number grid: c = real + imaginary * i
c = real_grid + 1j * imaginary_grid

# =============================================================================
# STEP 2: Initialize arrays for iteration
# =============================================================================

# z starts at 0 for each point (Mandelbrot set uses z_0 = 0)
z = np.zeros_like(c, dtype=np.complex128)

# Track how many iterations before each point "escapes"
# Points that never escape stay at max_iterations (these are IN the set)
iteration_count = np.zeros(c.shape, dtype=np.int32)

# =============================================================================
# STEP 3: The Mandelbrot Iteration Algorithm
# =============================================================================
# For each point c, repeatedly apply: z = z^2 + c
# A point "escapes" when |z| > 2 (it will diverge to infinity)
# Points that never escape belong to the Mandelbrot set

for i in range(max_iterations):
    # Create mask of points that haven't escaped yet
    # |z| <= 2 means the point is still "bounded"
    still_bounded = np.abs(z) <= 2

    # Apply the iteration formula ONLY to bounded points
    # z_{n+1} = z_n^2 + c
    z[still_bounded] = z[still_bounded] ** 2 + c[still_bounded]

    # Increment iteration count for points that haven't escaped
    iteration_count[still_bounded] += 1

# =============================================================================
# STEP 4: Map iteration counts to colors
# =============================================================================
# Points that escaped early (low iteration count) = bright colors
# Points that escaped late (high iteration count) = dark colors
# Points that never escaped (iteration_count = max_iterations) = black (in the set)

# Normalize iteration counts to 0-255 range for grayscale
normalized = (iteration_count / max_iterations * 255).astype(np.uint8)

# Create RGB image (we'll use a blue-to-white gradient)
# Points inside the Mandelbrot set will be black
image_array = np.zeros((height, width, 3), dtype=np.uint8)

# Color mapping: darker blue for low iterations, white for high iterations
# Points in the set (max iterations) will be black
mask_in_set = iteration_count == max_iterations
mask_outside = ~mask_in_set

# Outside the set: blue gradient based on escape time
image_array[mask_outside, 0] = (normalized[mask_outside] * 0.3).astype(np.uint8)  # Red
image_array[mask_outside, 1] = (normalized[mask_outside] * 0.5).astype(np.uint8)  # Green
image_array[mask_outside, 2] = normalized[mask_outside]                            # Blue

# Inside the set: black
image_array[mask_in_set] = [0, 0, 0]

# =============================================================================
# STEP 5: Save the result
# =============================================================================

output_image = Image.fromarray(image_array, mode='RGB')
output_image.save('mandelbrot_basic.png')
print(f"Mandelbrot set saved as 'mandelbrot_basic.png' ({width}x{height} pixels)")
print(f"Maximum iterations: {max_iterations}")
print(f"Viewing window: x=[{x_min}, {x_max}], y=[{y_min}, {y_max}]")
