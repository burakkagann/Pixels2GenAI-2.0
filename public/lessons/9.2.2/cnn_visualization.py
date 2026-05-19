import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Core Convolution Implementation
# =============================================================================

def convolve2d(image, kernel):
    """
    Perform 2D convolution on a grayscale image.

    This is the fundamental operation in CNNs - sliding a small filter
    (kernel) across an image and computing weighted sums at each position.

    Parameters
    ----------
    image : numpy.ndarray
        Input grayscale image (height, width)
    kernel : numpy.ndarray
        Convolution kernel/filter (kernel_height, kernel_width)

    Returns
    -------
    numpy.ndarray
        Convolved output image (smaller than input due to valid convolution)
    """
    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape

    # Calculate output dimensions (valid convolution - no padding)
    output_height = image_height - kernel_height + 1
    output_width = image_width - kernel_width + 1

    # Initialize output array
    output = np.zeros((output_height, output_width), dtype=np.float64)

    # Slide the kernel across the image
    for y in range(output_height):
        for x in range(output_width):
            # Extract the region under the kernel
            region = image[y:y+kernel_height, x:x+kernel_width]
            # Element-wise multiplication and sum
            output[y, x] = np.sum(region * kernel)

    return output

def normalize_for_display(image):
    """
    Normalize image values to 0-255 range for display.

    Parameters
    ----------
    image : numpy.ndarray
        Input image with arbitrary value range

    Returns
    -------
    numpy.ndarray
        Normalized image as uint8 (0-255)
    """
    # Handle edge case of constant image
    if image.max() == image.min():
        return np.zeros_like(image, dtype=np.uint8)

    # Scale to 0-255 range
    normalized = (image - image.min()) / (image.max() - image.min()) * 255
    return normalized.astype(np.uint8)

# =============================================================================
# Filter Kernels (Classical Image Processing Filters)
# =============================================================================

# Sobel filters for edge detection
SOBEL_X = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
], dtype=np.float64)

SOBEL_Y = np.array([
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
], dtype=np.float64)

# Gaussian blur (3x3 approximation)
GAUSSIAN_BLUR = np.array([
    [1, 2, 1],
    [2, 4, 2],
    [1, 2, 1]
], dtype=np.float64) / 16.0

# Sharpen filter
SHARPEN = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
], dtype=np.float64)

# Emboss filter (creates 3D shadow effect)
EMBOSS = np.array([
    [-2, -1, 0],
    [-1,  1, 1],
    [ 0,  1, 2]
], dtype=np.float64)

# Box blur (simple average)
BOX_BLUR = np.array([
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1]
], dtype=np.float64) / 9.0

# Laplacian (edge detection - second derivative)
LAPLACIAN = np.array([
    [0,  1, 0],
    [1, -4, 1],
    [0,  1, 0]
], dtype=np.float64)

# Identity kernel (no change)
IDENTITY = np.array([
    [0, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
], dtype=np.float64)

# Dictionary of all kernels for easy access
KERNELS = {
    'sobel_x': SOBEL_X,
    'sobel_y': SOBEL_Y,
    'gaussian': GAUSSIAN_BLUR,
    'sharpen': SHARPEN,
    'emboss': EMBOSS,
    'box_blur': BOX_BLUR,
    'laplacian': LAPLACIAN,
    'identity': IDENTITY
}

# =============================================================================
# Synthetic Test Pattern Generation
# =============================================================================

def create_checkerboard(size=256, square_size=32):
    """
    Create a checkerboard pattern for testing edge detection.

    Parameters
    ----------
    size : int
        Image dimensions (size x size)
    square_size : int
        Size of each checker square

    Returns
    -------
    numpy.ndarray
        Checkerboard pattern as grayscale image
    """
    image = np.zeros((size, size), dtype=np.float64)

    for y in range(size):
        for x in range(size):
            # Alternate colors based on position
            if ((x // square_size) + (y // square_size)) % 2 == 0:
                image[y, x] = 255.0

    return image

def create_gradient(size=256):
    """
    Create a horizontal gradient pattern.

    Parameters
    ----------
    size : int
        Image dimensions (size x size)

    Returns
    -------
    numpy.ndarray
        Gradient pattern from black (left) to white (right)
    """
    x = np.linspace(0, 255, size)
    image = np.tile(x, (size, 1))
    return image.astype(np.float64)

def create_concentric_circles(size=256, num_rings=8):
    """
    Create concentric circles pattern for testing radial edge detection.

    Parameters
    ----------
    size : int
        Image dimensions (size x size)
    num_rings : int
        Number of alternating rings

    Returns
    -------
    numpy.ndarray
        Concentric circles pattern
    """
    center_y, center_x = size // 2, size // 2
    y, x = np.ogrid[:size, :size]

    # Calculate distance from center
    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)

    # Create alternating rings
    ring_width = size / (2 * num_rings)
    pattern = ((distance / ring_width).astype(int) % 2) * 255.0

    return pattern.astype(np.float64)

def create_geometric_shapes(size=256):
    """
    Create an image with various geometric shapes for testing.

    Parameters
    ----------
    size : int
        Image dimensions (size x size)

    Returns
    -------
    numpy.ndarray
        Image containing rectangles, circles, and triangles
    """
    image = np.zeros((size, size), dtype=np.float64)

    # Rectangle in top-left
    image[30:90, 30:110] = 255

    # Circle in top-right
    center_y, center_x = 60, 190
    y, x = np.ogrid[:size, :size]
    mask = (x - center_x)**2 + (y - center_y)**2 <= 40**2
    image[mask] = 255

    # Triangle in bottom-left (filled)
    for row in range(150, 220):
        # Width increases as we go down
        width = (row - 150) * 2 // 3
        center = 70
        if width > 0:
            image[row, max(0, center-width):min(size, center+width)] = 255

    # Square with gradient in bottom-right
    y_start, x_start = 150, 150
    for dy in range(70):
        for dx in range(70):
            image[y_start + dy, x_start + dx] = 255 - (dy + dx) * 2

    return image

# =============================================================================
# Visualization Functions
# =============================================================================

def create_filter_comparison_grid(image, kernel_names=None):
    """
    Create a grid showing the same image processed by multiple filters.

    Parameters
    ----------
    image : numpy.ndarray
        Input grayscale image
    kernel_names : list of str, optional
        List of kernel names to use. If None, uses default set.

    Returns
    -------
    numpy.ndarray
        Grid image showing original and filtered versions
    """
    if kernel_names is None:
        kernel_names = ['sobel_x', 'sobel_y', 'gaussian', 'sharpen', 'emboss', 'laplacian']

    # Apply each filter
    results = []
    for name in kernel_names:
        kernel = KERNELS[name]
        filtered = convolve2d(image, kernel)
        normalized = normalize_for_display(filtered)
        results.append((name, normalized))

    # Create grid layout (2 rows x 3 cols)
    num_filters = len(results)
    cols = 3
    rows = (num_filters + cols - 1) // cols

    # Get consistent size (smallest output)
    min_height = min(r[1].shape[0] for r in results)
    min_width = min(r[1].shape[1] for r in results)

    # Padding and spacing
    pad = 10
    label_height = 25

    cell_width = min_width + 2 * pad
    cell_height = min_height + label_height + 2 * pad

    grid_width = cols * cell_width
    grid_height = rows * cell_height

    # Create white background
    grid = np.ones((grid_height, grid_width), dtype=np.uint8) * 255

    for idx, (name, filtered) in enumerate(results):
        row = idx // cols
        col = idx % cols

        x_start = col * cell_width + pad
        y_start = row * cell_height + label_height + pad

        # Crop to consistent size
        cropped = filtered[:min_height, :min_width]
        grid[y_start:y_start + min_height, x_start:x_start + min_width] = cropped

    return grid, results

def compute_edge_magnitude(image):
    """
    Compute edge magnitude using Sobel operators.

    This combines horizontal and vertical edge detection into
    a single edge magnitude image.

    Parameters
    ----------
    image : numpy.ndarray
        Input grayscale image

    Returns
    -------
    numpy.ndarray
        Edge magnitude image
    """
    # Apply Sobel filters
    edges_x = convolve2d(image, SOBEL_X)
    edges_y = convolve2d(image, SOBEL_Y)

    # Compute magnitude: sqrt(Gx^2 + Gy^2)
    magnitude = np.sqrt(edges_x**2 + edges_y**2)

    return normalize_for_display(magnitude)

# =============================================================================
# Main Visualization Script
# =============================================================================

def main():
    """Generate all visualization outputs for Module 9.2.2."""

    print("=" * 60)
    print("Module 9.2.2: Convolutional Networks Visualization")
    print("=" * 60)

    # Create test patterns
    print("\n[1/5] Creating synthetic test patterns...")
    checkerboard = create_checkerboard(256, 32)
    gradient = create_gradient(256)
    circles = create_concentric_circles(256, 8)
    shapes = create_geometric_shapes(256)

    # Save input patterns
    Image.fromarray(checkerboard.astype(np.uint8)).save(
        os.path.join(SCRIPT_DIR, 'input_checkerboard.png'))
    Image.fromarray(gradient.astype(np.uint8)).save(
        os.path.join(SCRIPT_DIR, 'input_gradient.png'))
    Image.fromarray(circles.astype(np.uint8)).save(
        os.path.join(SCRIPT_DIR, 'input_circles.png'))
    Image.fromarray(shapes.astype(np.uint8)).save(
        os.path.join(SCRIPT_DIR, 'input_shapes.png'))

    # Main edge detection output
    print("\n[2/5] Generating edge detection output...")
    edges_magnitude = compute_edge_magnitude(shapes)

    # Pad edges_magnitude to match original size for better comparison
    edge_h, edge_w = edges_magnitude.shape
    padded_edges = np.zeros((256, 256), dtype=np.uint8)
    pad_y = (256 - edge_h) // 2
    pad_x = (256 - edge_w) // 2
    padded_edges[pad_y:pad_y+edge_h, pad_x:pad_x+edge_w] = edges_magnitude

    # Create main output image showing original and edge-detected
    main_output = Image.new('RGB', (532, 256), color=(255, 255, 255))

    # Original image
    original_rgb = Image.fromarray(shapes.astype(np.uint8)).convert('RGB')
    main_output.paste(original_rgb, (0, 0))

    # Edge detected image
    edges_rgb = Image.fromarray(padded_edges).convert('RGB')
    main_output.paste(edges_rgb, (276, 0))

    main_output.save(os.path.join(SCRIPT_DIR, 'edge_detection_output.png'))
    print("   Saved: edge_detection_output.png")

    # Feature maps grid
    print("\n[3/5] Creating feature maps grid...")
    grid, results = create_filter_comparison_grid(shapes)
    Image.fromarray(grid).save(os.path.join(SCRIPT_DIR, 'feature_maps_grid.png'))
    print("   Saved: feature_maps_grid.png")

    # Individual filter outputs for detailed comparison
    print("\n[4/5] Generating individual filter outputs...")
    for kernel_name in ['sobel_x', 'sobel_y', 'sharpen', 'emboss']:
        kernel = KERNELS[kernel_name]
        filtered = convolve2d(shapes, kernel)
        normalized = normalize_for_display(filtered)
        Image.fromarray(normalized).save(
            os.path.join(SCRIPT_DIR, f'filter_{kernel_name}.png'))
        print(f"   Saved: filter_{kernel_name}.png")

    # Artistic filter combination
    print("\n[5/5] Creating artistic filter visualization...")

    # Apply sharpen then edge detection for artistic effect
    sharpened = convolve2d(circles, SHARPEN)
    artistic = compute_edge_magnitude(normalize_for_display(sharpened).astype(np.float64))

    # Create colorful version by mapping to RGB channels
    artistic_rgb = np.zeros((artistic.shape[0], artistic.shape[1], 3), dtype=np.uint8)
    artistic_rgb[:, :, 0] = artistic  # Red channel
    artistic_rgb[:, :, 1] = (255 - artistic)  # Inverted for green
    artistic_rgb[:, :, 2] = 128  # Constant blue

    Image.fromarray(artistic_rgb).save(os.path.join(SCRIPT_DIR, 'artistic_filters.png'))
    print("   Saved: artistic_filters.png")

    print("\n" + "=" * 60)
    print("All visualizations generated successfully!")
    print("=" * 60)

    # Print summary of convolution operation
    print("\n--- Convolution Example Summary ---")
    print(f"Input image size: {shapes.shape}")
    print(f"Kernel size: {SOBEL_X.shape}")
    print(f"Output size: {compute_edge_magnitude(shapes).shape}")
    print(f"Size reduction: {shapes.shape[0] - compute_edge_magnitude(shapes).shape[0]} pixels per edge")

if __name__ == '__main__':
    main()
