import numpy as np
from PIL import Image

# Image dimensions
height, width = 200, 200

# Start with a black image
image = np.zeros((height, width, 3), dtype=np.uint8)

# Build the gradient column by column
for col in range(width):

    # TODO 1: Calculate how far across the image this column is,
    #         as a value from 0 (left edge) to 255 (right edge).
    #         Hint: col * 255 // width
    proportion = ...

    # TODO 2: Set the red channel for this column.
    #         Red should be 255 at the left and 0 at the right.
    image[:, col, 0] = ...

    # TODO 3: Set the blue channel for this column.
    #         Blue should be 0 at the left and 255 at the right.
    image[:, col, 2] = ...

    # Green stays 0 (already set by np.zeros)

# Save the result
result = Image.fromarray(image, mode='RGB')
result.save('exercise3_gradient.png')
print("Saved exercise3_gradient.png")
print(f"Image shape: {image.shape}")

# ---------------------------------------------------------
# MAKE IT YOUR OWN (after completing the TODOs above):
#
#   - Change height and width to different values
#   - Try a vertical gradient (loop over rows instead)
#   - Try a yellow-to-cyan gradient (which channels change?)
#   - Try a diagonal gradient (use both row and col)
# ---------------------------------------------------------
