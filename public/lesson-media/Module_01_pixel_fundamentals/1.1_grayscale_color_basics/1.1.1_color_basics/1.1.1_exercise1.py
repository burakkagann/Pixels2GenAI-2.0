import numpy as np
from PIL import Image

# Create a 150x150 image
image = np.zeros((150, 150, 3), dtype=np.uint8)

# Set all pixels to the same color
image[:, :, 0] = 255  # Red channel
image[:, :, 1] = 128  # Green channel
image[:, :, 2] = 0    # Blue channel

# Save and inspect
Image.fromarray(image).save('exercise1_color.png')
