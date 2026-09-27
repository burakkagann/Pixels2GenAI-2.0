
import numpy as np
from PIL import Image

# Step 1: Create coordinate grids
# meshgrid creates 2D arrays of x and y coordinates for every pixel
height, width = 400, 400
y_coords, x_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')

# Step 2: Define triangle vertices
# We'll create a triangle with vertices at (200, 50), (50, 350), (350, 350)
# This is an isoceles triangle pointing upward

# Step 3: Define the three edges as line equations
# For each edge, we determine which side of the line is "inside" the triangle
# Line equation form: ax + by + c >= 0 (or <= 0)

# Edge 1: From (200, 50) to (50, 350) - left edge
# Edge 2: From (200, 50) to (350, 350) - right edge
# Edge 3: From (50, 350) to (350, 350) - bottom edge (y = 350)

# For the bottom edge: all points where y <= 350
edge_bottom = y_coords <= 350

# For left edge: from (200, 50) to (50, 350)
# Slope = (350-50)/(50-200) = 300/-150 = -2
# Line: y - 50 = -2(x - 200) => y = -2x + 450
# Inside triangle: y <= -2x + 450 => y + 2x <= 450
edge_left = y_coords + 2 * (x_coords - 200) >= 50 - 350 + 2 * (200 - 50)
# Simplified: points to the right of the left edge
edge_left = (x_coords - 50) * (350 - 50) - (y_coords - 350) * (50 - 200) >= 0

# For right edge: from (200, 50) to (350, 350)
# Points to the left of the right edge
edge_right = (x_coords - 200) * (350 - 50) - (y_coords - 50) * (350 - 200) <= 0

# Recalculate using a cleaner cross-product approach
# Point is inside triangle if it's on the correct side of all three edges
def edge_function(x, y, x1, y1, x2, y2):
    """Returns positive if point (x,y) is to the left of edge from (x1,y1) to (x2,y2)"""
    return (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)

# Triangle vertices (clockwise order)
v1 = (200, 50)   # top
v2 = (350, 350)  # bottom right
v3 = (50, 350)   # bottom left

# Check if each pixel is inside the triangle
# For clockwise vertices, inside points have edge_function <= 0 for all edges
inside_edge1 = edge_function(x_coords, y_coords, v1[0], v1[1], v2[0], v2[1]) <= 0
inside_edge2 = edge_function(x_coords, y_coords, v2[0], v2[1], v3[0], v3[1]) <= 0
inside_edge3 = edge_function(x_coords, y_coords, v3[0], v3[1], v1[0], v1[1]) <= 0

# Step 4: Combine conditions - pixel is inside triangle if inside all three edges
triangle_mask = inside_edge1 & inside_edge2 & inside_edge3

# Step 5: Create the image
canvas = np.zeros((height, width), dtype=np.uint8)
canvas[triangle_mask] = 255

# Save result
Image.fromarray(canvas).save('simple_triangle.png')
