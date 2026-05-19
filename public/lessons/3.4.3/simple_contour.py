import numpy as np
from PIL import Image

# Step 1: Create a coordinate grid (like a map)
size = 300
x = np.linspace(-5, 5, size)
y = np.linspace(-5, 5, size)
X, Y = np.meshgrid(x, y)

# Step 2: Create a single Gaussian "hill" centered at origin
height = np.exp(-(X**2 + Y**2) / 4)

# Step 3: Normalize to 0-1 range and quantize into 8 levels
normalized = (height - height.min()) / (height.max() - height.min())
contour = (normalized * 8).astype(np.uint8) * 32

# Step 4: Save the result
image = Image.fromarray(contour, mode='L')
image.save('simple_contour.png')
print("Done! Saved simple_contour.png - a stepped contour visualization")
