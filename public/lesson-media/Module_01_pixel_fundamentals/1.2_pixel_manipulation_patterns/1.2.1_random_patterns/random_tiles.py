

import numpy as np
from PIL import Image

# Create a 10x10 grid of random RGB colors
random_colors = np.random.randint(0, 256, size=(10, 10, 3), dtype=np.uint8)

# Scale each color to a 20x20 pixel tile using Kronecker product
scaling_matrix = np.ones((20, 20, 1), dtype=np.uint8)
image_array = np.kron(random_colors, scaling_matrix)

# Convert to image and save
result_image = Image.fromarray(image_array)
result_image.save('random_tiles.png')
