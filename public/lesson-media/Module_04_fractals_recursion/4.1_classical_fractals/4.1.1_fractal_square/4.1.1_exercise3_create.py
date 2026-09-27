import numpy as np
from PIL import Image

# =============================================
# CONFIGURATION — Experiment after completing TODOs
# =============================================
RECURSION_DEPTH = 3     # Try different depths once your fractal works
COLOR_CHANNEL = 1       # 0=Red, 1=Green, 2=Blue
COLOR_INCREMENT = 32    # Brightness per level
CANVAS_SIZE = 800       # Image size in pixels
# =============================================

def fractal_square(canvas, x_min, x_max, y_min, y_max, depth):
    # Divide the region into a 3x3 grid
    center_x_start = x_min + (x_max - x_min) // 3
    center_x_end = x_min + (x_max - x_min) * 2 // 3
    center_y_start = y_min + (y_max - y_min) // 3
    center_y_end = y_min + (y_max - y_min) * 2 // 3

    # Fill the center square (this part is done for you)
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, COLOR_CHANNEL] += COLOR_INCREMENT

    if depth > 0:
        # Each corner covers 2/3 of the parent region in both dimensions.
        # The corner boundaries overlap with the center — this overlap
        # is what creates the nested, self-similar pattern.

        # TODO 1: Top-left corner
        #   x range: from the left edge to the center-end
        #   y range: from the top edge to the center-end
        ...

        # TODO 2: Top-right corner
        #   x range: from the center-start to the right edge
        #   y range: from the top edge to the center-end
        ...

        # TODO 3: Bottom-left corner
        #   x range: from the left edge to the center-end
        #   y range: from the center-start to the bottom edge
        ...

        # TODO 4: Bottom-right corner
        #   x range: from the center-start to the right edge
        #   y range: from the center-start to the bottom edge
        ...

# Generate the fractal and save
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)
fractal_square(canvas, 0, CANVAS_SIZE, 0, CANVAS_SIZE, RECURSION_DEPTH)

image = Image.fromarray(canvas)
image.save("exercise3_fractal.png")
print(f"Saved exercise3_fractal.png (depth={RECURSION_DEPTH})")

# ---------------------------------------------------------
# MAKE IT YOUR OWN (after completing the TODOs above):
#
#   - Change RECURSION_DEPTH to 5 — how dense does it get?
#   - Set COLOR_CHANNEL to 0 for a red fractal
#   - Try COLOR_INCREMENT = 64 for higher contrast
#   - Use all three channels: add separate fill lines for
#     channels 0, 1, and 2 with different increment values
#   - What happens if you only recurse into 2 corners
#     instead of 4? (Comment out two of your TODO lines)
# ---------------------------------------------------------
