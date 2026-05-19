import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Grid configuration
CELL_SIZE = 256
GRID_COLS = 3
GRID_ROWS = 2
TOTAL_WIDTH = CELL_SIZE * GRID_COLS
TOTAL_HEIGHT = CELL_SIZE * GRID_ROWS + 40  # Extra space for labels

# Colors
BACKGROUND_COLOR = (15, 15, 25)
ROSE_COLORS = [
    (255, 100, 150),   # Pink for k=2
    (100, 200, 255),   # Light blue for k=3
    (255, 200, 100),   # Gold for k=4
    (150, 255, 150),   # Light green for k=5
    (200, 150, 255),   # Lavender for k=6
    (255, 150, 100),   # Coral for k=7
]

# K values to demonstrate (top row: even, bottom row: odd gives more variety)
K_VALUES = [2, 3, 4, 5, 6, 7]

# Create main canvas
canvas = Image.new('RGB', (TOTAL_WIDTH, TOTAL_HEIGHT), BACKGROUND_COLOR)

def draw_rose(draw, center_x, center_y, k, amplitude, color, num_points=500):
    """Draw a rose curve at the specified location."""
    theta = np.linspace(0, 2 * np.pi, num_points)
    r = amplitude * np.cos(k * theta)

    # Convert to Cartesian
    x = center_x + r * np.cos(theta)
    y = center_y + r * np.sin(theta)

    # Draw as connected line
    points = list(zip(x.astype(int), y.astype(int)))
    draw.line(points, fill=color, width=2)

def get_petal_count(k):
    """Return the number of petals for a given k value."""
    if k % 2 == 0:
        return 2 * k
    else:
        return k

# Draw each rose variation
draw = ImageDraw.Draw(canvas)
amplitude = CELL_SIZE // 2 - 30  # Leave margin

for i, k in enumerate(K_VALUES):
    row = i // GRID_COLS
    col = i % GRID_COLS

    # Calculate center of this cell
    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2

    # Draw the rose
    color = ROSE_COLORS[i]
    draw_rose(draw, center_x, center_y, k, amplitude, color)

    # Add label
    petal_count = get_petal_count(k)
    label = f"k={k} ({petal_count} petals)"

    # Draw label at bottom of cell
    text_y = (row + 1) * CELL_SIZE - 25
    # Simple text centering using approximate character width
    text_x = center_x - len(label) * 4
    draw.text((text_x, text_y), label, fill=(200, 200, 200))

# Add title row at the bottom
title = "Rose Curve Variations: r = a * cos(k * theta)"
title_x = TOTAL_WIDTH // 2 - len(title) * 4
draw.text((title_x, TOTAL_HEIGHT - 30), title, fill=(255, 255, 255))

# Save result
output_path = SCRIPT_DIR / 'rose_variations.png'
canvas.save(output_path)
