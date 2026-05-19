import numpy as np
from PIL import Image

# =============================================================================
# TODO: Implement sigmoid function
# =============================================================================
def sigmoid(x):
    """
    Sigmoid activation function.

    Formula: f(x) = 1 / (1 + e^(-x))
    Output range: (0, 1)

    Parameters:
        x: Input array (can be any shape)

    Returns:
        Array of same shape with values between 0 and 1
    """
    pass  # Replace with your implementation

# =============================================================================
# TODO: Implement one more activation function of your choice
# =============================================================================
def my_activation(x):
    """
    Your custom activation function.

    Choose one of:
    - Leaky ReLU: max(0.1*x, x)
    - ELU: x if x > 0 else alpha * (exp(x) - 1)
    - Softplus: log(1 + exp(x))
    - Or design your own!

    Parameters:
        x: Input array

    Returns:
        Transformed array
    """
    pass  # Replace with your implementation

# =============================================================================
# Create coordinate grid
# =============================================================================
width, height = 512, 512
x = np.linspace(-5, 5, width)
y = np.linspace(-5, 5, height)
X, Y = np.meshgrid(x, y)

# =============================================================================
# TODO: Create an interesting input pattern
# =============================================================================
# Don't just use distance from center (sqrt(X**2 + Y**2))
# Try something creative:
#   - Waves: np.sin(X * 3) * np.cos(Y * 3)
#   - Diagonal: X + Y
#   - Hyperbolic: X * Y
#   - Checkerboard: np.sin(X * 5) * np.sin(Y * 5)
#   - Spiral: np.arctan2(Y, X) + np.sqrt(X**2 + Y**2)

input_pattern = None  # Replace with your pattern

# =============================================================================
# TODO: Apply your activation functions to create color channels
# =============================================================================
# Remember:
#   - Sigmoid outputs (0, 1), multiply by 255 for color
#   - Tanh outputs (-1, 1), shift and scale: (tanh(x) + 1) / 2 * 255
#   - ReLU is unbounded, need to normalize or clip
#   - Be creative! Mix functions, add offsets, use different scales

red = None    # Use one of your activations
green = None  # Use another activation or combination
blue = None   # Create an interesting blue channel

# =============================================================================
# Combine and save
# =============================================================================
image = np.zeros((height, width, 3), dtype=np.uint8)
image[:, :, 0] = np.clip(red, 0, 255).astype(np.uint8)
image[:, :, 1] = np.clip(green, 0, 255).astype(np.uint8)
image[:, :, 2] = np.clip(blue, 0, 255).astype(np.uint8)

Image.fromarray(image).save('my_activation_art.png')
print("Saved my_activation_art.png")
