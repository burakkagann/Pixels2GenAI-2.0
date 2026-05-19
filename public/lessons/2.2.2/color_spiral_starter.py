
import numpy as np
from PIL import Image

# Image setup
width, height = 512, 512
center_x, center_y = width // 2, height // 2
image = np.zeros((height, width, 3), dtype=np.uint8)

# Define start and end colors for the gradient
start_color = np.array([255, 50, 50])    # Red at center
end_color = np.array([50, 50, 255])      # Blue at edge

def spiral_generator(start_radius, growth_rate, num_points):
    """
    Generate spiral points with progress tracking.

    TODO: Modify this generator to yield (x, y, progress)
    where progress goes from 0.0 (center) to 1.0 (edge)
    """
    for i in range(num_points):
        angle = i * 0.1
        radius = start_radius + growth_rate * angle

        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))

        # TODO: Calculate progress (hint: i / num_points gives 0 to 1)
        progress = 0  # Replace this!

        yield x, y, progress

def interpolate_color(color1, color2, t):
    """
    Blend between two colors based on t (0 to 1).

    TODO: Implement linear interpolation between color1 and color2
    When t=0, return color1. When t=1, return color2.
    """
    # TODO: Replace this with actual interpolation
    return color1  # Currently just returns the start color

def draw_line(img, x1, y1, x2, y2, color):
    """Draw a line between two points."""
    distance = max(abs(x2 - x1), abs(y2 - y1), 1)

    for step in range(distance + 1):
        t = step / distance if distance > 0 else 0
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))

        if 0 <= x < width and 0 <= y < height:
            img[y, x] = color

# Generate and draw the spiral
spiral = spiral_generator(start_radius=5, growth_rate=0.5, num_points=500)
prev_x, prev_y, prev_progress = next(spiral)

for x, y, progress in spiral:
    # TODO: Get the interpolated color based on progress
    color = interpolate_color(start_color, end_color, progress)

    draw_line(image, prev_x, prev_y, x, y, color)
    prev_x, prev_y, prev_progress = x, y, progress

# Save result
output = Image.fromarray(image, mode='RGB')
output.save('color_spiral.png')

