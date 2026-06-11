
import numpy as np
from PIL import Image

def draw_line(canvas, x_start, y_start, x_end, y_end):
    """
    Draw a line on the canvas from (x_start, y_start) to (x_end, y_end).

    Uses parametric interpolation via np.linspace to calculate all points
    along the line, then sets those pixels to white (255).

    Parameters:
        canvas: 2D NumPy array representing grayscale image
        x_start, y_start: Starting coordinates
        x_end, y_end: Ending coordinates
    """
    # Calculate how many points we need (at least one per pixel)
    num_points = max(abs(x_end - x_start) + 1, abs(y_end - y_start) + 1)

    # Generate evenly-spaced coordinates
    x_coords = np.linspace(x_start, x_end, num_points).round().astype(int)
    y_coords = np.linspace(y_start, y_end, num_points).round().astype(int)

    # Set pixels to white
    canvas[y_coords, x_coords] = 255

# Create blank 400x400 canvas
canvas = np.zeros((400, 400), dtype=np.uint8)

# Draw radial lines emanating from a fixed point
# Each line goes from (50, 200) to a different point on the right edge
fixed_x, fixed_y = 50, 200  # Anchor point on left side
target_x = 350  # All lines end at x=350

# Create 9 lines with evenly-spaced endpoints along right edge
for target_y in range(0, 400, 50):
    draw_line(canvas, fixed_x, fixed_y, target_x, target_y)

# Save result
output_image = Image.fromarray(canvas)
output_image.save('line_pattern.png')
