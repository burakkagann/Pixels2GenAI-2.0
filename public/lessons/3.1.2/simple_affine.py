import numpy as np
from PIL import Image

# Create a blank canvas
canvas_size = 400
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
canvas[:] = [30, 30, 40]  # Dark background

# Define a simple square shape (as corner points)
# Original square: 100x100 pixels centered at origin
square_points = np.array([
    [-50, -50],  # Top-left
    [50, -50],   # Top-right
    [50, 50],    # Bottom-right
    [-50, 50],   # Bottom-left
], dtype=np.float64)

# Move original square to center of left half of canvas
original_offset = np.array([100, 200])
original_points = square_points + original_offset

# Define the affine transformation matrix
# Scale by 1.5x and translate to right side
scale_factor = 1.5
translate_x = 200
translate_y = 0

# The 2D affine matrix: [scale, 0, tx; 0, scale, ty]
# Applied as: new_point = scale * point + translation
affine_matrix = np.array([
    [scale_factor, 0, translate_x],
    [0, scale_factor, translate_y]
])

# Apply transformation: convert to homogeneous coords, then transform
# Add column of 1s for homogeneous coordinates
ones = np.ones((square_points.shape[0], 1))
homogeneous_points = np.hstack([square_points, ones])

# Apply affine transformation
transformed = (affine_matrix @ homogeneous_points.T).T
transformed_points = transformed + original_offset

# Helper function to draw a filled polygon
def draw_polygon(canvas, points, color):
    """Draw a filled polygon using scanline approach."""
    from PIL import Image, ImageDraw
    # Create a temporary image for drawing
    temp = Image.fromarray(canvas)
    draw = ImageDraw.Draw(temp)
    # Convert points to list of tuples
    pts = [(int(p[0]), int(p[1])) for p in points]
    draw.polygon(pts, fill=tuple(color))
    return np.array(temp)

# Draw original square (blue)
canvas = draw_polygon(canvas, original_points, [70, 130, 200])

# Draw transformed square (orange)
canvas = draw_polygon(canvas, transformed_points, [230, 150, 50])

# Add labels using simple text positioning
# (In a real application, you might use matplotlib for text)

# Save the result
output = Image.fromarray(canvas)
output.save('simple_affine.png')
