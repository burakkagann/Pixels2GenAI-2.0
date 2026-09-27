import numpy as np
from PIL import Image

# Set seed for reproducible randomness
np.random.seed(42)

# Create 10x10 grid of random RGB colors
random_colors = np.random.randint(0, 256, size=(10, 10, 3), dtype=np.uint8)

# Scale each color to a 20x20 pixel tile using Kronecker product
scaled_image = np.kron(random_colors, np.ones((20, 20, 1), dtype=np.uint8))

# Save the result
result = Image.fromarray(scaled_image)
result.save('quick_random_tiles.png')
