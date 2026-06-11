import numpy as np
from PIL import Image

# Step 1: Create a blank 150x150 image with 3 color channels
# np.zeros fills every pixel with 0 (black)
image = np.zeros((150, 150, 3), dtype=np.uint8)

# Step 2: Set the color of every pixel
# image[:, :, channel] sets ALL rows and ALL columns for one channel
image[:, :, 0] = 255  # Red channel   — full intensity
image[:, :, 1] = 128  # Green channel — half intensity
image[:, :, 2] = 0    # Blue channel  — off

# Step 3: Save the result
result = Image.fromarray(image, mode='RGB')
result.save('exercise1_color.png')
print("Saved exercise1_color.png")
# f-strings (f"...") insert variable values inside {braces}
print(f"Image shape: {image.shape}  (height, width, channels)")
print(f"Pixel color: R={image[0, 0, 0]}, G={image[0, 0, 1]}, B={image[0, 0, 2]}")
