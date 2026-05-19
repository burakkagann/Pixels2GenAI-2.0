import numpy as np
import imageio.v2 as imageio

# =============================================================================
# Configuration - You can modify these values
# =============================================================================

WIDTH = 400               # Image width (smaller for faster testing)
HEIGHT = 400              # Image height
NUM_FRAMES = 30           # Number of frames (start small, increase later)
FRAMES_PER_SECOND = 24    # Animation playback speed
MAX_ITERATIONS = 150      # Mandelbrot iteration limit

# Zoom target coordinates (try different locations!)
# Seahorse Valley (default): CENTER_X = -0.743644, CENTER_Y = 0.131826
# Elephant Valley: CENTER_X = 0.275, CENTER_Y = 0.0
# Mini Mandelbrot: CENTER_X = -1.768, CENTER_Y = 0.0
CENTER_X = -0.743644
CENTER_Y = 0.131826

INITIAL_WIDTH = 3.0       # Starting view width
ZOOM_FACTOR = 100         # Final zoom level

# =============================================================================
# TODO: Implement these functions
# =============================================================================

def compute_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iter):
    """
    Compute Mandelbrot set iteration counts for a rectangular region.

    The Mandelbrot set is defined by the iteration:
        z(n+1) = z(n)^2 + c
    starting from z(0) = 0. A point c is in the set if the sequence
    does not escape to infinity (|z| stays <= 2).

    Parameters:
        width, height: Image dimensions in pixels
        x_min, x_max: Horizontal bounds in complex plane (real axis)
        y_min, y_max: Vertical bounds in complex plane (imaginary axis)
        max_iter: Maximum iterations before assuming point is in set

    Returns:
        2D numpy array of iteration counts (height x width)
    """
    # TODO Step 1: Create coordinate arrays
    # Use np.linspace to create 'width' evenly spaced values from x_min to x_max
    # Use np.linspace to create 'height' evenly spaced values from y_min to y_max
    real_values = ...  # TODO: np.linspace(x_min, x_max, width)
    imag_values = ...  # TODO: np.linspace(y_min, y_max, height)

    # TODO Step 2: Create 2D grids using np.meshgrid
    # This gives us the coordinates for every pixel
    real_grid, imag_grid = ...  # TODO: np.meshgrid(real_values, imag_values)

    # TODO Step 3: Combine into complex number array
    # Each pixel corresponds to a complex number c = real + i*imag
    c_values = ...  # TODO: real_grid + 1j * imag_grid

    # TODO Step 4: Initialize z values (start at 0) and iteration counter
    z_values = np.zeros_like(c_values, dtype=complex)
    iteration_counts = np.zeros(c_values.shape, dtype=float)

    # TODO Step 5: Iterate the Mandelbrot formula
    for iteration in range(max_iter):
        # Find points that haven't escaped yet (|z| <= 2)
        still_iterating = ...  # TODO: np.abs(z_values) <= 2

        # Update z = z^2 + c for non-escaped points
        z_values[still_iterating] = ...  # TODO: z_values[still_iterating] ** 2 + c_values[still_iterating]

        # Record this iteration number for points still inside
        iteration_counts[still_iterating] = iteration

    return iteration_counts

def iterations_to_colors(iteration_counts, max_iter):
    """
    Convert iteration counts to RGB colors.

    Points that reached max_iter are inside the Mandelbrot set (color black).
    Other points are colored based on how quickly they escaped.

    Parameters:
        iteration_counts: 2D array of iteration values
        max_iter: Maximum iteration count used

    Returns:
        3D array of RGB values (height, width, 3), dtype=uint8
    """
    # Normalize to 0-1 range
    normalized = iteration_counts / max_iter

    # Create output array
    height, width = iteration_counts.shape
    colors = np.zeros((height, width, 3), dtype=np.uint8)

    # TODO Step 6: Identify points inside the set (reached max iterations)
    inside_set = ...  # TODO: iteration_counts >= (max_iter - 1)

    # TODO Step 7: Assign colors
    # Points inside set should be black (0, 0, 0)
    # Points outside get a color gradient based on normalized value
    # Example: Red = normalized * 200, Green = normalized * 100, Blue = 255 - normalized * 200
    colors[:, :, 0] = ...  # TODO: Red channel
    colors[:, :, 1] = ...  # TODO: Green channel
    colors[:, :, 2] = ...  # TODO: Blue channel

    return colors

def calculate_zoom_window(frame_index, total_frames, center_x, center_y,
                          initial_width, zoom_factor):
    """
    Calculate the view window bounds for a specific frame.

    Uses exponential interpolation so zoom speed appears constant.
    The formula is: current_width = initial_width * zoom_factor^(-progress)

    Parameters:
        frame_index: Current frame (0 to total_frames-1)
        total_frames: Total number of frames
        center_x, center_y: Zoom target coordinates
        initial_width: Starting view width
        zoom_factor: How much to zoom in by final frame

    Returns:
        Tuple of (x_min, x_max, y_min, y_max)
    """
    # TODO Step 8: Calculate progress (0 to 1)
    progress = ...  # TODO: frame_index / (total_frames - 1)

    # TODO Step 9: Calculate current width using exponential zoom
    # Formula: current_width = initial_width * (zoom_factor ** (-progress))
    current_width = ...  # TODO

    # Maintain square aspect ratio
    current_height = current_width

    # TODO Step 10: Calculate window bounds centered on target
    x_min = ...  # TODO: center_x - current_width / 2
    x_max = ...  # TODO: center_x + current_width / 2
    y_min = ...  # TODO: center_y - current_height / 2
    y_max = ...  # TODO: center_y + current_height / 2

    return x_min, x_max, y_min, y_max

# =============================================================================
# Animation Generation (This part is complete - no changes needed)
# =============================================================================

def generate_animation():
    """Generate the Mandelbrot zoom animation using your implemented functions."""
    print(f"Generating {NUM_FRAMES} frame animation...")
    print(f"Zoom target: ({CENTER_X}, {CENTER_Y})")

    frames = []

    for frame_index in range(NUM_FRAMES):
        # Get view window for this frame
        x_min, x_max, y_min, y_max = calculate_zoom_window(
            frame_index, NUM_FRAMES, CENTER_X, CENTER_Y,
            INITIAL_WIDTH, ZOOM_FACTOR
        )

        # Compute Mandelbrot
        iterations = compute_mandelbrot(
            WIDTH, HEIGHT, x_min, x_max, y_min, y_max, MAX_ITERATIONS
        )

        # Convert to colors
        frame_colors = iterations_to_colors(iterations, MAX_ITERATIONS)
        frames.append(frame_colors)

        # Progress indicator
        if frame_index % 10 == 0:
            print(f"Frame {frame_index + 1}/{NUM_FRAMES}")

    # Save animation
    imageio.mimsave('my_fractal_animation.gif', frames, fps=FRAMES_PER_SECOND, loop=0)
    print("Saved: my_fractal_animation.gif")

if __name__ == '__main__':
    generate_animation()
