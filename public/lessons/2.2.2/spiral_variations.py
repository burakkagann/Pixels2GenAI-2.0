
import numpy as np
from PIL import Image, ImageDraw

# Each cell in the 2x2 grid
cell_size = 256
grid_size = 2
total_size = cell_size * grid_size  # 512x512

def spiral_generator(center_x, center_y, start_radius, growth_rate, angle_step, num_points):
    """
    Generate points along an Archimedean spiral with customizable parameters.

    Parameters:
        center_x, center_y: Center point of the spiral
        start_radius: Initial distance from center (a in r = a + b*theta)
        growth_rate: How fast radius increases per radian (b in r = a + b*theta)
        angle_step: Angle increment per point (controls density)
        num_points: Total number of points to generate
    """
    for i in range(num_points):
        angle = i * angle_step
        radius = start_radius + growth_rate * angle

        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))

        yield x, y

def draw_line(img, x1, y1, x2, y2, color, bounds):
    """Draw a line within specified bounds."""
    min_x, min_y, max_x, max_y = bounds
    distance = max(abs(x2 - x1), abs(y2 - y1), 1)

    for step in range(distance + 1):
        t = step / distance if distance > 0 else 0
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))

        if min_x <= x < max_x and min_y <= y < max_y:
            img[y, x] = color

def draw_spiral_in_cell(img, cell_row, cell_col, params, color):
    """Draw a spiral in a specific grid cell."""
    # Calculate cell boundaries
    offset_x = cell_col * cell_size
    offset_y = cell_row * cell_size
    center_x = offset_x + cell_size // 2
    center_y = offset_y + cell_size // 2

    bounds = (offset_x, offset_y, offset_x + cell_size, offset_y + cell_size)

    # Generate spiral points
    spiral = spiral_generator(
        center_x, center_y,
        params['start_radius'],
        params['growth_rate'],
        params['angle_step'],
        params['num_points']
    )

    # Draw connecting lines
    prev_x, prev_y = next(spiral)
    for x, y in spiral:
        draw_line(img, prev_x, prev_y, x, y, color, bounds)
        prev_x, prev_y = x, y

# Create canvas with dark background
image = np.zeros((total_size, total_size, 3), dtype=np.uint8)
image[:, :] = [15, 15, 25]

# Define four different parameter sets
variations = [
    # Top-left: Tight spiral (small growth rate)
    {
        'name': 'Tight Spiral',
        'start_radius': 5,
        'growth_rate': 1.6,
        'angle_step': 0.1,
        'num_points': 600,
        'color': [100, 200, 255]  # Light blue
    },
    # Top-right: Loose spiral (large growth rate)
    {
        'name': 'Loose Spiral',
        'start_radius': 5,
        'growth_rate': 3.2,
        'angle_step': 0.1,
        'num_points': 300,
        'color': [255, 150, 100]  # Orange
    },
    # Bottom-left: Dense spiral (small angle step)
    {
        'name': 'Dense Spiral',
        'start_radius': 10,
        'growth_rate': 2.2,
        'angle_step': 0.05,
        'num_points': 800,
        'color': [150, 255, 150]  # Light green
    },
    # Bottom-right: Sparse spiral (large angle step)
    {
        'name': 'Sparse Spiral',
        'start_radius': 10,
        'growth_rate': 1.5,
        'angle_step': 0.3,
        'num_points': 200,
        'color': [255, 200, 100]  # Yellow
    }
]

# Draw each spiral in its cell
positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
for (row, col), params in zip(positions, variations):
    draw_spiral_in_cell(image, row, col, params, params['color'])

# Add grid lines to separate cells
pil_image = Image.fromarray(image, mode='RGB')
draw = ImageDraw.Draw(pil_image)

# Vertical line
draw.line([(cell_size, 0), (cell_size, total_size)], fill=(60, 60, 80), width=2)
# Horizontal line
draw.line([(0, cell_size), (total_size, cell_size)], fill=(60, 60, 80), width=2)

# Add labels
labels = ['Tight (growth=1.6)', 'Loose (growth=3.2)',
          'Dense (step=0.05)', 'Sparse (step=0.3)']
label_positions = [(10, 10), (cell_size + 10, 10),
                   (10, cell_size + 10), (cell_size + 10, cell_size + 10)]

for label, pos in zip(labels, label_positions):
    draw.text(pos, label, fill=(180, 180, 180))

# Save result
result = np.array(pil_image)
output = Image.fromarray(result, mode='RGB')
output.save('spiral_variations.png')
