import numpy as np
from PIL import Image

# Discrete color palette (values divisible by 32)
color_palette = np.array([0, 32, 64, 96, 128, 160, 192, 224])

# Generate random indices into the palette for a 16x16 grid
random_indices = np.random.randint(0, len(color_palette), size=(16, 16, 3))

# Map indices to actual color values
small_array = color_palette[random_indices].astype(np.uint8)

# Scale each color to 12x12 pixel tiles
scaling_matrix = np.ones((12, 12, 1), dtype=np.uint8)
image_array = np.kron(small_array, scaling_matrix)

# Save result
result_image = Image.fromarray(image_array)
result_image.save('richter_style.png')
print(f"Created {image_array.shape} Richter-style grid!")
