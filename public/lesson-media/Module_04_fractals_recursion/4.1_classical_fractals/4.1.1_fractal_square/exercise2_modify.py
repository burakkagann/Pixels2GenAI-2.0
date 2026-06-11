import numpy as np
from PIL import Image

# =============================================
# CONFIGURATION — Modify these values
# =============================================
RECURSION_DEPTH = 3     # How many levels of detail (try 0, 1, 2, 3, 4, 5)
COLOR_CHANNEL = 1       # Which RGB channel: 0=Red, 1=Green, 2=Blue
COLOR_INCREMENT = 32    # Brightness added per level (try 16, 32, 64)
CANVAS_SIZE = 800       # Image dimensions in pixels
# =============================================

def draw_fractal_square(canvas, x_min, x_max, y_min, y_max, depth):
    x_third = (x_max - x_min) // 3
    y_third = (y_max - y_min) // 3

    center_x_start = x_min + x_third
    center_x_end = x_min + 2 * x_third
    center_y_start = y_min + y_third
    center_y_end = y_min + 2 * y_third

    # Fill the center square on the chosen color channel
    canvas[center_y_start:center_y_end, center_x_start:center_x_end, COLOR_CHANNEL] += COLOR_INCREMENT

    if depth > 0:
        draw_fractal_square(canvas, x_min, center_x_end, y_min, center_y_end, depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max, y_min, center_y_end, depth - 1)
        draw_fractal_square(canvas, x_min, center_x_end, center_y_start, y_max, depth - 1)
        draw_fractal_square(canvas, center_x_start, x_max, center_y_start, y_max, depth - 1)

# Create the canvas and generate the fractal
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8)
draw_fractal_square(canvas, 0, CANVAS_SIZE, 0, CANVAS_SIZE, RECURSION_DEPTH)

# Save result
channel_names = {0: "Red", 1: "Green", 2: "Blue"}
channel_name = channel_names.get(COLOR_CHANNEL, "Unknown")

image = Image.fromarray(canvas)
image.save("exercise2_result.png")

print(f"Saved exercise2_result.png")
print(f"  Depth: {RECURSION_DEPTH}  |  Channel: {channel_name}  |  Increment: {COLOR_INCREMENT}")
