import numpy as np
from PIL import Image

def draw_fractal_square(canvas, x_min, x_max, y_min, y_max, depth):
    # Calculate one-third of the region dimensions using integer division.
    # The // operator (floor division) ensures pixel coordinates stay as
    # whole numbers — regular / would give floats, which cannot index arrays.
    x_third = (x_max - x_min) // 3
    y_third = (y_max - y_min) // 3

    # Locate the center square boundaries within the 3x3 grid
    center_x_start = x_min + x_third
    center_x_end = x_min + 2 * x_third
    center_y_start = y_min + y_third
    center_y_end = y_min + 2 * y_third

    # Fill the center square by adding 32 to the green channel.
    #
    # canvas[y1:y2, x1:x2, 1] is NumPy array slicing:
    #   - y1:y2 selects rows (vertical range)
    #   - x1:x2 selects columns (horizontal range)
    #   - 1 selects the green channel (0=Red, 1=Green, 2=Blue)
    #
    # The += operator adds a value to every element in the slice at once.
    # Where regions overlap, color accumulates — brighter areas show more
    # recursion levels stacking on top of each other.
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, 1] += 32

    # Base case: stop when depth reaches 0
    # Recursive case: apply the same process to each corner
    if depth > 0:
        draw_fractal_square(canvas, x_min, center_x_end, y_min, center_y_end, depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max, y_min, center_y_end, depth - 1)
        draw_fractal_square(canvas, x_min, center_x_end, center_y_start, y_max, depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max, center_y_start, y_max, depth - 1)

# np.zeros(shape, dtype) creates an array filled with zeros.
# Shape (800, 800, 3) means: 800 rows, 800 columns, 3 color channels (RGB).
# dtype=np.uint8 stores each value as an unsigned 8-bit integer (range 0-255),
# which matches the standard range for image pixel values.
canvas_size = 800
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# Generate the fractal with 4 levels of recursion
recursion_depth = 5
draw_fractal_square(canvas, 0, canvas_size, 0, canvas_size, recursion_depth)

# Image.fromarray() converts a NumPy array into a PIL Image object,
# which can then be saved as PNG, JPEG, or other image formats.
image = Image.fromarray(canvas)
image.save("exercise1_fractal.png")

print(f"Saved exercise1_fractal.png ({canvas_size}x{canvas_size}, depth={recursion_depth})")
