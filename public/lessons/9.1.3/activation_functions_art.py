import numpy as np
from PIL import Image

# =============================================================================
# Activation Functions (implemented from scratch using NumPy)
# =============================================================================

def sigmoid(x):
    """
    Sigmoid activation: squashes any input to range (0, 1).

    Formula: f(x) = 1 / (1 + e^(-x))

    Properties:
    - Smooth, S-shaped curve
    - Output always between 0 and 1 (like probability)
    - Historically popular but can cause vanishing gradients
    """
    return 1.0 / (1.0 + np.exp(-x))

def relu(x):
    """
    ReLU (Rectified Linear Unit): keeps positive values, zeros negatives.

    Formula: f(x) = max(0, x)

    Properties:
    - Simple and computationally efficient
    - Creates sparse activations (many zeros)
    - Most popular activation in modern deep learning
    """
    return np.maximum(0, x)

def tanh_activation(x):
    """
    Hyperbolic tangent: squashes input to range (-1, 1).

    Formula: f(x) = tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))

    Properties:
    - Zero-centered (outputs can be negative)
    - Similar shape to sigmoid but scaled
    - Good for hidden layers in some architectures
    """
    return np.tanh(x)

# =============================================================================
# Image Generation
# =============================================================================

# Image dimensions
width, height = 512, 512

# Step 1: Create a coordinate grid
# x and y range from -5 to 5 (good range to see activation behavior)
x = np.linspace(-5, 5, width)
y = np.linspace(-5, 5, height)
X, Y = np.meshgrid(x, y)

# Step 2: Calculate distance from center (creates radial patterns)
# This gives us a circular gradient that we'll transform with activations
distance = np.sqrt(X**2 + Y**2)

# Step 3: Apply activation functions to create different color channels
# Each function transforms the distance differently, creating unique patterns
red_channel = sigmoid(distance - 2.5) * 255       # Smooth transition at r=2.5
green_channel = relu(3 - distance) / 3 * 255      # Bright center, dark outside
blue_channel = (tanh_activation(distance - 2) + 1) / 2 * 255  # Smooth bands

# Step 4: Combine channels into RGB image
image_array = np.zeros((height, width, 3), dtype=np.uint8)
image_array[:, :, 0] = red_channel.astype(np.uint8)
image_array[:, :, 1] = green_channel.astype(np.uint8)
image_array[:, :, 2] = blue_channel.astype(np.uint8)

# Step 5: Save the result
output = Image.fromarray(image_array, mode='RGB')
output.save('activation_art.png')
print("Saved activation_art.png (512x512)")
print("  Red channel:   sigmoid(distance - 2.5)")
print("  Green channel: relu(3 - distance)")
print("  Blue channel:  tanh(distance - 2)")
