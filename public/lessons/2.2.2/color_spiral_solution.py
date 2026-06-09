
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

    Yields (x, y, progress) where progress goes from 0.0 to 1.0
    as the spiral moves from center to edge.
    """
    for i in range(num_points):
        angle = i * 0.1
        radius = start_radius + growth_rate * angle

        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))

        # Calculate progress: 0 at start, 1 at end
        progress = i / (num_points - 1) if num_points > 1 else 0

        yield x, y, progress

def interpolate_color(color1, color2, t):
    """
    Blend between two colors based on t (0 to 1).

    Linear interpolation: result = color1 * (1-t) + color2 * t
    When t=0: returns color1
    When t=1: returns color2
    When t=0.5: returns the midpoint between both colors
    """
    # Ensure t is clamped between 0 and 1
    t = max(0, min(1, t))

    # Linear interpolation formula
    blended = color1 * (1 - t) + color2 * t

    # Convert to integers for pixel values
    return blended.astype(np.uint8)

def draw_line(img, x1, y1, x2, y2, color):
    """Draw a line between two points using linear interpolation."""
    distance = max(abs(x2 - x1), abs(y2 - y1), 1)

    for step in range(distance + 1):
        t = step / distance if distance > 0 else 0
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))

        if 0 <= x < width and 0 <= y < height:
            img[y, x] = color

# Generate and draw the color gradient spiral
spiral = spiral_generator(start_radius=10, growth_rate=4.0, num_points=500)
prev_x, prev_y, prev_progress = next(spiral)

for x, y, progress in spiral:
    # Get the interpolated color based on how far along the spiral we are
    color = interpolate_color(start_color, end_color, progress)

    draw_line(image, prev_x, prev_y, x, y, color)
    prev_x, prev_y, prev_progress = x, y, progress

# Save result
output = Image.fromarray(image, mode='RGB')
output.save('color_spiral.png')
