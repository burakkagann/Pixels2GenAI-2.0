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

# Pendulum parameters (5:4 ratio creates interesting pattern)
FREQ_X = 5
FREQ_Y = 4
AMP_X = 200
AMP_Y = 200
PHASE_Y = np.pi / 2
DAMPING = 0.003
NUM_POINTS = 5000

# Color gradient: from bright cyan to deep blue
START_COLOR = (100, 255, 255)    # Bright cyan (high energy)
END_COLOR = (20, 40, 80)         # Dark blue (low energy)

# =============================================================================
# Step 1: Generate time array and calculate oscillations
# =============================================================================
t = np.linspace(0, 100, NUM_POINTS)
decay = np.exp(-DAMPING * t)

# Calculate x and y positions with damping
x = CENTER + AMP_X * np.sin(FREQ_X * t) * decay
y = CENTER + AMP_Y * np.sin(FREQ_Y * t + PHASE_Y) * decay

# =============================================================================
# Step 2: Create canvas
# =============================================================================
image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# =============================================================================
# Step 3: Helper function to interpolate color based on decay
# =============================================================================
def get_faded_color(decay_value):
    """
    Interpolate between START_COLOR (decay=1) and END_COLOR (decay=0).

    Args:
        decay_value: Float from 0 to 1, where 1 is full energy, 0 is fully decayed

    Returns:
        RGB tuple with interpolated color
    """
    r = int(START_COLOR[0] * decay_value + END_COLOR[0] * (1 - decay_value))
    g = int(START_COLOR[1] * decay_value + END_COLOR[1] * (1 - decay_value))
    b = int(START_COLOR[2] * decay_value + END_COLOR[2] * (1 - decay_value))
    return (r, g, b)

# =============================================================================
# Step 4: Draw harmonograph with color fading
# =============================================================================
for i in range(1, len(t)):
    # Calculate color based on current decay value
    color = get_faded_color(decay[i])

    # Draw line segment from previous point to current point
    x1, y1 = int(x[i-1]), int(y[i-1])
    x2, y2 = int(x[i]), int(y[i])
    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

# =============================================================================
# Step 5: Save the result
# =============================================================================
output_path = SCRIPT_DIR / 'colored_harmonograph_solution.png'
image.save(output_path)