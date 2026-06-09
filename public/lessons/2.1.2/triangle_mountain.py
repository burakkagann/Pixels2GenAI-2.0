
import numpy as np
from PIL import Image

def draw_filled_triangle(canvas, v1, v2, v3, color):
    """
    Fill a triangle defined by three vertices with a given color.

    Uses the edge function approach: a point is inside the triangle if
    it's on the correct side of all three edges.

    Parameters:
        canvas: numpy array to draw on (height, width, 3) for RGB
        v1, v2, v3: tuple of (x, y) coordinates for each vertex
        color: tuple of (R, G, B) values
    """
    height, width = canvas.shape[:2]
    y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

    def edge_function(x, y, x1, y1, x2, y2):
        """Check which side of an edge a point lies on"""
        return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

    # Check all three edges (vertices in clockwise order)
    e1 = edge_function(x_coords, y_coords, v1[0], v1[1], v2[0], v2[1])
    e2 = edge_function(x_coords, y_coords, v2[0], v2[1], v3[0], v3[1])
    e3 = edge_function(x_coords, y_coords, v3[0], v3[1], v1[0], v1[1])

    # Point is inside if all edge functions have same sign
    inside = (e1 <= 0) & (e2 <= 0) & (e3 <= 0)

    # Fill the triangle
    canvas[inside] = color

def create_gradient_sky(height, width):
    """
    Create a vertical gradient from deep blue (top) to orange (horizon).

    Returns:
        numpy array of shape (height, width, 3) with RGB gradient
    """
    sky = np.zeros((height, width, 3), dtype=np.uint8)

    # Define colors: deep blue at top, warm orange at bottom
    top_color = np.array([25, 25, 112])      # Midnight blue
    bottom_color = np.array([255, 140, 50])  # Sunset orange

    # Create gradient by interpolating between colors
    for y in range(height):
        t = y / height  # 0 at top, 1 at bottom
        color = (1 - t) * top_color + t * bottom_color
        sky[y, :] = color.astype(np.uint8)

    return sky

# Step 1: Create canvas with gradient sky background
height, width = 400, 500
canvas = create_gradient_sky(height, width)

# Step 2: Define mountains (from back to front for proper layering)
# Each mountain: (peak_x, peak_y, left_base_x, right_base_x, color)
mountains = [
    # Background mountain (lighter, more distant)
    {
        'peak': (400, 80),
        'left': (250, 400),
        'right': (500, 400),
        'color': (100, 100, 120)  # Distant gray-blue
    },
    # Middle mountain (medium tone)
    {
        'peak': (150, 120),
        'left': (0, 400),
        'right': (320, 400),
        'color': (70, 80, 90)  # Medium gray
    },
    # Foreground mountain (darkest, closest)
    {
        'peak': (300, 180),
        'left': (150, 400),
        'right': (480, 400),
        'color': (40, 45, 50)  # Dark silhouette
    },
    # Small foreground peak
    {
        'peak': (80, 250),
        'left': (0, 400),
        'right': (200, 400),
        'color': (30, 35, 40)  # Darkest
    },
]

# Step 3: Draw mountains from back to front
for mountain in mountains:
    draw_filled_triangle(
        canvas,
        mountain['peak'],
        mountain['right'],  # Clockwise order
        mountain['left'],
        mountain['color']
    )

# Step 4: Save result
Image.fromarray(canvas).save('triangle_mountain.png')

