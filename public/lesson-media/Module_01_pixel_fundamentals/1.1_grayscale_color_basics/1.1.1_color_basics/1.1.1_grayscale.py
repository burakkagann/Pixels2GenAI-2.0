import numpy as np
from PIL import Image

# Create a 200x200 array filled with medium gray
array = np.zeros((200, 200), dtype=np.uint8)
array += 128

# PIL interprets 2D arrays as grayscale automatically
image = Image.fromarray(array)
image.save('gray.png')
