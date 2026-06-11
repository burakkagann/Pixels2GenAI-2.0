import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

# =============================================================================
# Configuration
# =============================================================================
CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
BACKGROUND_COLOR = (10, 10, 20)

# Pendulum parameters
FREQ_X = 5
FREQ_Y = 4
AMP_X = 200
AMP_Y = 200
PHASE_Y = np.pi / 2
DAMPING = 0.003
NUM_POINTS = 5000

# Base color (bright version - will fade from this)
BASE_COLOR = (100, 255, 255)  # Bright cyan

# =============================================================================
# Step 1: Generate time array and oscillations
# =============================================================================
t = np.linspace(0, 100, NUM_POINTS)
decay = np.exp(-DAMPING * t)

x = CENTER + AMP_X * np.sin(FREQ_X * t) * decay
y = CENTER + AMP_Y * np.sin(FREQ_Y * t + PHASE_Y) * decay

# =============================================================================
# Step 2: Create canvas
# =============================================================================
image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# =============================================================================
# TODO: Draw the harmonograph with fading color
# =============================================================================
# Currently draws single-color line (your task: add color fading)

# Option 1: Simple approach (no fading - current implementation)
# points = list(zip(x.astype(int), y.astype(int)))
# draw.line(points, fill=BASE_COLOR, width=1)

# Option 2: YOUR CODE HERE - Draw segments with fading color
# Hint: Loop through points and calculate color based on decay[i]

for i in range(1, len(t)):
    # TODO: Calculate faded color based on decay[i]
    # Hint: faded_color = tuple(int(c * decay[i]) for c in BASE_COLOR)
    color = BASE_COLOR  # Replace this with your fading color calculation

    # Draw line segment
    draw.line([(int(x[i-1]), int(y[i-1])), (int(x[i]), int(y[i]))],
              fill=color, width=1)

# =============================================================================
# Save result
# =============================================================================
output_path = SCRIPT_DIR / 'my_colored_harmonograph.png'
image.save(output_path)
