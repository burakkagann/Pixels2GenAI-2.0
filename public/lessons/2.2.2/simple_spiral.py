
import numpy as np
from PIL import Image

# Image dimensions and center point
width, height = 512, 512
center_x, center_y = width // 2, height // 2

# Create a black canvas
image = np.zeros((height, width, 3), dtype=np.uint8)

def spiral_generator(start_radius=10, growth_rate=4.0, num_points=500):
    """
    Generate points along an Archimedean spiral.

    The Archimedean spiral follows the formula: r = a + b * theta
    where 'a' is the starting radius and 'b' controls how fast it grows.

    Yields (x, y) coordinates for each point on the spiral.
    """
    for i in range(num_points):
        # Calculate angle in radians (multiple rotations)
        angle = i * 0.1  # Controls how tightly wound the spiral is

        # Archimedean spiral: radius grows linearly with angle
        radius = start_radius + growth_rate * angle

        # Convert polar (radius, angle) to Cartesian (x, y)
        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))

        yield x, y

def draw_line(img, x1, y1, x2, y2, color):
    """Draw a line between two points using linear interpolation."""
    # Calculate number of steps based on distance
    distance = max(abs(x2 - x1), abs(y2 - y1), 1)

    for step in range(distance + 1):
        t = step / distance if distance > 0 else 0
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))

        # Check bounds before drawing
        if 0 <= x < width and 0 <= y < height:
            img[y, x] = color

# Generate spiral points and connect them with lines
spiral = spiral_generator(start_radius=10, growth_rate=4.0, num_points=500)
prev_x, prev_y = next(spiral)  # Get first point

# Draw the spiral by connecting consecutive points
white = [255, 255, 255]
for x, y in spiral:
    draw_line(image, prev_x, prev_y, x, y, white)
    prev_x, prev_y = x, y

# Save the result
output = Image.fromarray(image, mode='RGB')
output.save('simple_spiral.png')
