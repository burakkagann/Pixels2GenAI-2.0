import numpy as np
from PIL import Image

# Create a 200x200 image with 3 color channels (RGB)
image = np.zeros((200, 200, 3), dtype=np.uint8)

# Top half: cyan
image[:100, :, 1] = 255  # Green channel
image[:100, :, 2] = 255  # Blue channel

# Bottom half: magenta
image[100:, :, 0] = 255  # Red channel
image[100:, :, 2] = 255  # Blue channel

# Convert to PIL and save
pil_image = Image.fromarray(image)
pil_image.save('cyan_magenta.png')
