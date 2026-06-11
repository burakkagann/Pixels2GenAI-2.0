import numpy as np
from PIL import Image
import os

# =============================================================================
# CONFIG -- change this AFTER completing the TODOs to experiment
# =============================================================================
# Choose a kernel: 'edge', 'blur', 'sharpen', or 'identity'
KERNEL_CHOICE = 'edge'

KERNELS = {
    'edge': np.array([
        [-1, -1, -1],
        [-1,  8, -1],
        [-1, -1, -1]
    ], dtype=np.float64),

    'blur': np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ], dtype=np.float64) / 9.0,

    'sharpen': np.array([
        [ 0, -1,  0],
        [-1,  5, -1],
        [ 0, -1,  0]
    ], dtype=np.float64),

    'identity': np.array([
        [0, 0, 0],
        [0, 1, 0],
        [0, 0, 0]
    ], dtype=np.float64),
}
# =============================================================================

kernel = KERNELS[KERNEL_CHOICE]

# =============================================================================
# Step 1: Load the Brandenburg Gate image
# =============================================================================
# The image is stored in the same folder as this script.
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bbtor.jpg')

img = Image.open(IMAGE_PATH).convert('L')
img = img.resize((256, 171))

# np.array() converts a PIL image into a NumPy array of pixel values.
image = np.array(img, dtype=np.float64)
print(f"Loaded Brandenburg Gate image: {image.shape[1]}x{image.shape[0]} pixels")

print(f"\nUsing kernel: {KERNEL_CHOICE}")
print(kernel)

# =============================================================================
# Step 2: Complete this function!
# =============================================================================
def apply_convolution(image, kernel):
    """
    Apply a convolution kernel to a grayscale image.

    For each pixel, extract the surrounding region, multiply it by the
    kernel weights, and sum to get the output value.

    Parameters:
        image (np.ndarray): 2D array of pixel values (grayscale)
        kernel (np.ndarray): 2D array of kernel weights (e.g., 3x3)

    Returns:
        np.ndarray: Convolved image (same size as input)
    """
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2

    height, width = image.shape

    # np.zeros() creates an array of the given shape filled with zeros.
    # We use it to prepare an empty output image.
    output = np.zeros((height, width), dtype=np.float64)

    # np.pad() adds extra rows and columns around the image so the kernel
    # can process edge pixels without going out of bounds.
    # mode='edge' copies the outermost pixel values outward.
    padded = np.pad(image, pad, mode='edge')

    # TODO 1: Loop over every row in the image.

    # TODO 2: Inside that loop, loop over every column.

    # TODO 3: Extract the region under the kernel using array slicing.
    #         The region starts at (y, x) in the padded image and has
    #         the same size as the kernel.

    # TODO 4: Compute the output pixel by multiplying the region by the
    #         kernel (element-wise) and summing all values.
    #         np.sum() adds up every element in an array.

    return output

# =============================================================================
# Step 3: Test your implementation
# =============================================================================
if __name__ == '__main__':
    print("\nApplying your convolution function...")

    result = apply_convolution(image, kernel)

    # np.clip() restricts all values to the range [0, 255].
    # Edge detection can produce negatives and values above 255.
    result = np.clip(result, 0, 255).astype(np.uint8)

    output_image = Image.fromarray(result, mode='L')
    output_image.save('exercise3_result.png')

    print("Saved exercise3_result.png")

    if np.max(result) == 0:
        print("\nThe output is all black -- the TODOs are not filled in yet.")
        print("Open this file and complete TODO 1 through TODO 4.")
    else:
        print("Your convolution is working!")

    # =========================================================================
    # MAKE IT YOUR OWN -- try these after completing the TODOs
    # =========================================================================
    # 1. Change KERNEL_CHOICE at the top to 'blur', 'sharpen', or 'identity'
    #    and re-run to compare effects.
    #
    # 2. Design your own kernel! Replace KERNEL_CHOICE with a custom array:
    #
    #    Horizontal edge detector (finds horizontal lines):
    #        kernel = np.array([[-1,-1,-1], [2,2,2], [-1,-1,-1]], dtype=np.float64)
    #
    #    Vertical edge detector (finds vertical lines):
    #        kernel = np.array([[-1,2,-1], [-1,2,-1], [-1,2,-1]], dtype=np.float64)
    #
    #    Emboss (3D illusion, lit from top-left):
    #        kernel = np.array([[-2,-1,0], [-1,1,1], [0,1,2]], dtype=np.float64)
    #
    # 3. Try a 5x5 blur kernel: np.ones((5, 5)) / 25.0
    #    How does it compare to the 3x3 version?
