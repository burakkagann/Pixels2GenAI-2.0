import numpy as np
import imageio.v2 as imageio
from PIL import Image

# =============================================================================
# Configuration Parameters
# =============================================================================

# Canvas dimensions
WIDTH = 512
HEIGHT = 512

# Animation settings
NUM_FRAMES = 60           # Total frames in animation
FRAMES_PER_SECOND = 30    # Playback speed

# Mandelbrot computation
MAX_ITERATIONS = 200      # Higher = more detail, slower computation

# Zoom target: "Seahorse Valley" - a famous region with intricate spirals
# These coordinates were discovered by early fractal explorers
CENTER_X = -0.743643887037158704752191506114774
CENTER_Y = 0.131825904205311970493132056385139

# Zoom parameters
INITIAL_WIDTH = 3.0       # Starting view width (shows full set)
ZOOM_FACTOR = 500         # How much to zoom in by final frame

# =============================================================================
# Fractal Generation Functions
# =============================================================================

def compute_mandelbrot(width, height, x_min, x_max, y_min, y_max, max_iter):
    """
    Compute Mandelbrot set iteration counts for a rectangular region.

    Uses vectorized NumPy operations for efficient computation. The Mandelbrot
    set is defined as the set of complex numbers c for which the iteration
    z(n+1) = z(n)^2 + c does not diverge to infinity.

    Parameters:
        width, height: Image dimensions in pixels
        x_min, x_max: Horizontal bounds in complex plane
        y_min, y_max: Vertical bounds in complex plane
        max_iter: Maximum iterations before assuming convergence

    Returns:
        2D array of iteration counts (0 to max_iter)
    """
    # Create coordinate grids for the complex plane
    real_values = np.linspace(x_min, x_max, width)
    imag_values = np.linspace(y_min, y_max, height)
    real_grid, imag_grid = np.meshgrid(real_values, imag_values)

    # Combine into complex number array: c = real + i*imag
    c_values = real_grid + 1j * imag_grid

    # Initialize iteration variables
    z_values = np.zeros_like(c_values, dtype=complex)
    iteration_counts = np.zeros(c_values.shape, dtype=float)

    # Iterate the Mandelbrot formula: z = z^2 + c
    for iteration in range(max_iter):
        # Find points that haven't escaped yet (|z| <= 2)
        still_iterating = np.abs(z_values) <= 2

        # Update z values only for non-escaped points
        z_values[still_iterating] = (z_values[still_iterating] ** 2 +
                                     c_values[still_iterating])

        # Record iteration count for points still inside
        iteration_counts[still_iterating] = iteration

    return iteration_counts

def iterations_to_colors(iteration_counts, max_iter):
    """
    Convert iteration counts to RGB colors using a smooth gradient.

    Points inside the Mandelbrot set (max iterations) are colored black.
    Points outside are colored based on how quickly they escaped, creating
    the characteristic colorful boundary regions.

    Parameters:
        iteration_counts: 2D array of iteration values
        max_iter: Maximum iteration count used in computation

    Returns:
        3D array of RGB values (height, width, 3)
    """
    # Normalize iteration counts to 0-1 range
    normalized = iteration_counts / max_iter

    # Create RGB image array
    height, width = iteration_counts.shape
    colors = np.zeros((height, width, 3), dtype=np.uint8)

    # Points that reached max iterations are inside the set (black)
    inside_set = iteration_counts >= (max_iter - 1)

    # Color the boundary using a blue-gold gradient
    # This creates visually pleasing contrast
    colors[:, :, 0] = np.where(inside_set, 0, (normalized * 255 * 0.8).astype(np.uint8))  # Red
    colors[:, :, 1] = np.where(inside_set, 0, (normalized * 255 * 0.5).astype(np.uint8))  # Green
    colors[:, :, 2] = np.where(inside_set, 0, (255 - normalized * 200).astype(np.uint8))  # Blue

    return colors

def calculate_zoom_window(frame_index, total_frames, center_x, center_y,
                          initial_width, zoom_factor):
    """
    Calculate the view window for a specific frame using exponential zoom.

    Exponential zoom creates smooth, visually pleasing animations where
    the zoom speed appears constant to the viewer. Linear zoom would
    make early frames feel slow and late frames feel rushed.

    Parameters:
        frame_index: Current frame number (0-based)
        total_frames: Total frames in animation
        center_x, center_y: Zoom target coordinates
        initial_width: Starting view width
        zoom_factor: Total zoom multiplier by final frame

    Returns:
        Tuple of (x_min, x_max, y_min, y_max) defining view bounds
    """
    # Calculate progress through animation (0 to 1)
    progress = frame_index / (total_frames - 1) if total_frames > 1 else 0

    # Exponential interpolation: width shrinks exponentially
    current_width = initial_width * (zoom_factor ** (-progress))
    current_height = current_width * (HEIGHT / WIDTH)  # Maintain aspect ratio

    # Calculate bounds centered on target point
    x_min = center_x - current_width / 2
    x_max = center_x + current_width / 2
    y_min = center_y - current_height / 2
    y_max = center_y + current_height / 2

    return x_min, x_max, y_min, y_max

# =============================================================================
# Animation Generation
# =============================================================================

def generate_animation():
    """
    Generate the complete Mandelbrot zoom animation.

    Creates frames one by one, each showing a deeper zoom level,
    then combines them into an animated GIF.
    """
    print(f"Generating {NUM_FRAMES} frame Mandelbrot zoom animation...")
    print(f"Resolution: {WIDTH}x{HEIGHT}, Max iterations: {MAX_ITERATIONS}")
    print(f"Zoom target: ({CENTER_X:.6f}, {CENTER_Y:.6f})")
    print(f"Zoom factor: {ZOOM_FACTOR}x")
    print()

    frames = []

    for frame_index in range(NUM_FRAMES):
        # Calculate view window for this frame
        x_min, x_max, y_min, y_max = calculate_zoom_window(
            frame_index, NUM_FRAMES, CENTER_X, CENTER_Y,
            INITIAL_WIDTH, ZOOM_FACTOR
        )

        # Compute Mandelbrot iteration counts
        iterations = compute_mandelbrot(
            WIDTH, HEIGHT, x_min, x_max, y_min, y_max, MAX_ITERATIONS
        )

        # Convert to colors
        frame_colors = iterations_to_colors(iterations, MAX_ITERATIONS)
        frames.append(frame_colors)

        # Progress indicator
        if frame_index % 10 == 0 or frame_index == NUM_FRAMES - 1:
            current_zoom = ZOOM_FACTOR ** (frame_index / (NUM_FRAMES - 1))
            print(f"Frame {frame_index + 1}/{NUM_FRAMES} - Zoom: {current_zoom:.1f}x")

    # Save as animated GIF
    print("\nSaving animation...")
    imageio.mimsave('animated_fractal.gif', frames, fps=FRAMES_PER_SECOND, loop=0)
    print("Saved: animated_fractal.gif")

    # Save key frames as static image for documentation
    save_frame_comparison(frames)

    return frames

def save_frame_comparison(frames):
    """
    Save a comparison image showing frames at different zoom levels.

    This helps learners understand the zoom progression without
    needing to watch the full animation.
    """
    # Select frames: start, middle, end
    indices = [0, NUM_FRAMES // 2, NUM_FRAMES - 1]
    labels = ["Start (1x)", f"Middle ({ZOOM_FACTOR**(0.5):.0f}x)", f"End ({ZOOM_FACTOR}x)"]

    # Create comparison image (3 frames side by side)
    comparison = np.zeros((HEIGHT, WIDTH * 3, 3), dtype=np.uint8)

    for i, idx in enumerate(indices):
        comparison[:, i * WIDTH:(i + 1) * WIDTH, :] = frames[idx]

    Image.fromarray(comparison).save('mandelbrot_frames.png')
    print("Saved: mandelbrot_frames.png (frame comparison)")

# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    generate_animation()
    print("\nAnimation complete! Open animated_fractal.gif to view.")
