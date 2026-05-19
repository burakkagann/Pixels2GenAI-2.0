import numpy as np
from PIL import Image, ImageDraw

def create_square(size=30):
    """Create a square centered at origin."""
    half = size / 2
    return np.array([
        [-half, -half],
        [half, -half],
        [half, half],
        [-half, half]
    ], dtype=np.float64)

def make_rotation_matrix(angle_degrees):
    """Create a 3x3 rotation matrix."""
    theta = np.radians(angle_degrees)
    return np.array([
        [np.cos(theta), -np.sin(theta), 0],
        [np.sin(theta), np.cos(theta), 0],
        [0, 0, 1]
    ])

def make_scale_matrix(sx, sy):
    """Create a 3x3 scaling matrix."""
    return np.array([
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1]
    ])

def make_translation_matrix(tx, ty):
    """Create a 3x3 translation matrix."""
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])

def apply_transform(points, matrix):
    """Apply 3x3 transformation matrix to points."""
    # Add homogeneous coordinate
    ones = np.ones((points.shape[0], 1))
    homogeneous = np.hstack([points, ones])
    # Apply transformation and extract x,y
    transformed = (matrix @ homogeneous.T).T
    return transformed[:, :2]

def combine_transforms(*matrices):
    """Combine multiple transformation matrices (right to left order)."""
    result = np.eye(3)
    for matrix in matrices:
        result = result @ matrix
    return result

# Create canvas
canvas_size = 500
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
canvas[:] = [20, 20, 30]  # Dark background

# Create PIL image for drawing
pil_image = Image.fromarray(canvas)
draw = ImageDraw.Draw(pil_image)

# Base square
square = create_square(size=25)

# Create a spiral pattern of transformed squares
# Each iteration: rotate a bit more, scale slightly smaller, move outward
center = canvas_size // 2
num_shapes = 24

for i in range(num_shapes):
    # Calculate transformation parameters for this iteration
    angle = i * 15  # 15 degrees per shape
    scale = 1.0 - (i * 0.02)  # Gradually get smaller
    scale = max(scale, 0.3)  # Don't go below 0.3
    distance = 50 + i * 6  # Spiral outward

    # Build the combined transformation
    # Order: first rotate around origin, then scale, then translate to position
    rotation = make_rotation_matrix(angle)
    scaling = make_scale_matrix(scale, scale)

    # Calculate position on spiral
    spiral_x = center + distance * np.cos(np.radians(angle * 2))
    spiral_y = center + distance * np.sin(np.radians(angle * 2))
    translation = make_translation_matrix(spiral_x, spiral_y)

    # Combine: Translation @ Scaling @ Rotation
    # (Read right to left: rotate, then scale, then translate)
    combined = combine_transforms(translation, scaling, rotation)

    # Apply to square
    transformed = apply_transform(square, combined)

    # Color gradient from blue to orange
    t = i / (num_shapes - 1)
    r = int(70 + t * 180)
    g = int(130 - t * 50)
    b = int(200 - t * 150)

    # Draw the shape
    polygon_points = [(int(p[0]), int(p[1])) for p in transformed]
    draw.polygon(polygon_points, fill=(r, g, b), outline=(255, 255, 255))

# Convert back to numpy and save
result = np.array(pil_image)
Image.fromarray(result).save('combined_transform_output.png')