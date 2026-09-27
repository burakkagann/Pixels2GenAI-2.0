import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# =============================================================================
# Grid configuration
# =============================================================================
CELL_SIZE = 256                 # Size of each harmonograph cell
GRID_COLS = 3
GRID_ROWS = 2
TOTAL_WIDTH = CELL_SIZE * GRID_COLS
TOTAL_HEIGHT = CELL_SIZE * GRID_ROWS + 40  # Extra space for labels

BACKGROUND_COLOR = (10, 10, 20)

# Different frequency ratio combinations to demonstrate
# Format: (freq_x, freq_y, color, label)
VARIATIONS = [
    (1, 1, (255, 150, 150), "1:1 (Circle)"),
    (2, 1, (255, 200, 100), "2:1 (Figure-8)"),
    (3, 2, (150, 255, 150), "3:2"),
    (3, 4, (100, 200, 255), "3:4"),
    (5, 4, (200, 150, 255), "5:4"),
    (7, 5, (255, 200, 200), "7:5 (Complex)"),
]

# Common parameters for all harmonographs
AMPLITUDE = 100             # Fits within cell
DAMPING = 0.003             # Moderate damping
NUM_POINTS = 5000
PHASE_Y = np.pi / 2         # 90-degree phase difference

def draw_harmonograph(draw, center_x, center_y, freq_x, freq_y, amplitude, color):
    """
    Draw a single harmonograph pattern centered at the given position.

    Args:
        draw: ImageDraw object
        center_x, center_y: Center position for this harmonograph
        freq_x, freq_y: Frequency of x and y pendulums
        amplitude: Maximum displacement from center
        color: RGB tuple for the line color
    """
    # Generate time array
    t = np.linspace(0, 100, NUM_POINTS)

    # Calculate damped oscillations
    decay = np.exp(-DAMPING * t)
    x = amplitude * np.sin(freq_x * t) * decay
    y = amplitude * np.sin(freq_y * t + PHASE_Y) * decay

    # Convert to canvas coordinates
    canvas_x = center_x + x
    canvas_y = center_y + y

    # Draw the curve
    points = list(zip(canvas_x.astype(int), canvas_y.astype(int)))
    draw.line(points, fill=color, width=1)

# =============================================================================
# Create the comparison grid
# =============================================================================
image = Image.new('RGB', (TOTAL_WIDTH, TOTAL_HEIGHT), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# Draw each harmonograph variation
for i, (freq_x, freq_y, color, label) in enumerate(VARIATIONS):
    row = i // GRID_COLS
    col = i % GRID_COLS

    # Calculate center of this cell
    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2

    # Draw the harmonograph
    draw_harmonograph(draw, center_x, center_y, freq_x, freq_y, AMPLITUDE, color)

    # Draw cell border (subtle)
    border_color = (40, 40, 60)
    draw.rectangle([col * CELL_SIZE, row * CELL_SIZE,
                    (col + 1) * CELL_SIZE - 1, (row + 1) * CELL_SIZE - 1],
                   outline=border_color)

    # Add label at bottom of cell
    label_y = row * CELL_SIZE + CELL_SIZE - 20
    draw.text((center_x, label_y), label, fill=(200, 200, 200), anchor="mm")

# Add title at bottom
title_y = GRID_ROWS * CELL_SIZE + 20
draw.text((TOTAL_WIDTH // 2, title_y),
          "Harmonograph Patterns: Effect of Frequency Ratios",
          fill=(200, 200, 200), anchor="mm")

# =============================================================================
# Save the result
# =============================================================================
output_path = SCRIPT_DIR / 'harmonograph_variations.png'
image.save(output_path)