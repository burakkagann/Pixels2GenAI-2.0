import numpy as np
from PIL import Image
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def convolve2d(image, kernel):
    """
    Perform 2D convolution on a grayscale image.

    Parameters
    ----------
    image : numpy.ndarray
        Input grayscale image (height, width)
    kernel : numpy.ndarray
        Convolution kernel/filter (kernel_height, kernel_width)

    Returns
    -------
    numpy.ndarray
        Convolved output image
    """
    image_height, image_width = image.shape
    kernel_height, kernel_width = kernel.shape

    # TODO: Calculate output dimensions
    # Hint: output_height = image_height - kernel_height + 1
    output_height = None  # Replace with correct formula
    output_width = None   # Replace with correct formula

    # TODO: Initialize output array with zeros
    output = None  # Replace

    # TODO: Implement the convolution loops
    # Slide the kernel across the image
    for y in range(output_height):
        for x in range(output_width):
            # TODO: Extract the region under the kernel
            # Hint: region = image[y:y+kernel_height, x:x+kernel_width]
            region = None  # Replace

            # TODO: Compute element-wise multiplication and sum
            # Hint: output[y, x] = np.sum(region * kernel)
            pass  # Replace with calculation

    return output

def normalize_for_display(image):
    """
    Normalize image values to 0-255 range for display.
    """
    if image.max() == image.min():
        return np.zeros_like(image, dtype=np.uint8)

    normalized = (image - image.min()) / (image.max() - image.min()) * 255
    return normalized.astype(np.uint8)

def create_test_pattern(size=256):
    """
    Create a checkerboard pattern for testing.
    """
    pattern = np.zeros((size, size), dtype=np.float64)
    square_size = 32

    for y in range(size):
        for x in range(size):
            if ((x // square_size) + (y // square_size)) % 2 == 0:
                pattern[y, x] = 255.0

    return pattern

# =============================================================================
# Main Exercise
# =============================================================================

if __name__ == '__main__':

    # Step 1: Create test pattern
    print("Creating test pattern...")
    pattern = create_test_pattern(256)

    # Step 2: Define your custom artistic kernel
    # TODO: Create your own 3x3 filter kernel
    # Ideas:
    #   - Diagonal edge detector: detects edges at 45 degrees
    #   - Emboss with different direction
    #   - Custom gradient detector

    # Example: Diagonal edge detector
    my_kernel = np.array([
        # TODO: Fill in your kernel values
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ], dtype=np.float64)

    # Step 3: Apply your filter
    print("Applying custom filter...")
    result = convolve2d(pattern, my_kernel)

    if result is not None:
        # Step 4: Normalize for display
        display_result = normalize_for_display(result)

        # Step 5: Save result
        output_path = os.path.join(SCRIPT_DIR, 'my_filter_output.png')
        Image.fromarray(display_result).save(output_path)
        print(f"Saved result to: {output_path}")

        # Print statistics
        print(f"\nInput shape: {pattern.shape}")
        print(f"Kernel shape: {my_kernel.shape}")
        print(f"Output shape: {result.shape}")
        print(f"Output value range: [{result.min():.2f}, {result.max():.2f}]")
    else:
        print("Error: convolve2d returned None. Check your implementation.")
