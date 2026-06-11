import numpy as np
from PIL import Image

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def softplus(x):
    """Smooth approximation of ReLU: log(1 + e^x)"""
    return np.log1p(np.exp(np.clip(x, -20, 20)))

width, height = 512, 512

x = np.linspace(-5, 5, width)
y = np.linspace(-3, 3, height)
X, Y = np.meshgrid(x, y)

# Aurora pattern: vertical waves with horizontal flow
# Multiple sine waves at different frequencies create organic movement
wave1 = np.sin(X * 1.5 + Y * 2)
wave2 = np.sin(X * 0.8 - Y * 1.2) * 0.5
wave3 = np.cos(X * 2 + Y * 0.5) * 0.3
combined_wave = wave1 + wave2 + wave3

# Vertical gradient (aurora tends to be brighter at top)
vertical_fade = sigmoid((Y + 1) * 2)

# Apply activations with aurora-like colors
# Green dominates (typical aurora color), with hints of purple and blue
green = sigmoid(combined_wave * 2) * vertical_fade * 255
blue = softplus(combined_wave) / 3 * vertical_fade * 200
red = sigmoid(combined_wave - 1) * vertical_fade * 100

# Add a dark base at the bottom
darkness = sigmoid(-Y * 3) * 0.8
green = green * (1 - darkness)
blue = blue * (1 - darkness * 0.5)
red = red * (1 - darkness * 0.7)

image_array = np.zeros((height, width, 3), dtype=np.uint8)
image_array[:, :, 0] = np.clip(red, 0, 255).astype(np.uint8)
image_array[:, :, 1] = np.clip(green, 0, 255).astype(np.uint8)
image_array[:, :, 2] = np.clip(blue, 0, 255).astype(np.uint8)

output = Image.fromarray(image_array, mode='RGB')
output.save('challenge_aurora.png')
print("Saved challenge_aurora.png")
