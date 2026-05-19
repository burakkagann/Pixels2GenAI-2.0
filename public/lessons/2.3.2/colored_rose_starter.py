
import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Canvas settings
CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
BACKGROUND_COLOR = (15, 15, 25)

# Rose curve parameters
K_PARAMETER = 5      # Creates 5 petals
AMPLITUDE = 180
NUM_POINTS = 1000

# Color palette for 5 petals
PETAL_COLORS = [
    (255, 100, 100),   # Red
    (255, 200, 100),   # Orange
    (255, 255, 100),   # Yellow
    (100, 255, 100),   # Green
    (100, 100, 255),   # Blue
]

# Create canvas
image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# Generate rose curve points
theta = np.linspace(0, 2 * np.pi, NUM_POINTS)
r = AMPLITUDE * np.cos(K_PARAMETER * theta)

# Convert to Cartesian coordinates
x = CENTER + r * np.cos(theta)
y = CENTER + r * np.sin(theta)

# TODO: Implement color selection based on angle
# Hint 1: Each petal corresponds to a range of theta values
# Hint 2: Use the relationship between theta and petal index
# Hint 3: Consider using modulo (%) to cycle through colors

def get_petal_color(theta_value, k):
    """
    Determine which petal color to use based on the angle.

    Args:
        theta_value: Current angle in radians (0 to 2*pi)
        k: The k parameter of the rose curve

    Returns:
        tuple: RGB color for this position

    TODO: Implement this function!
    The petal index should depend on where we are in the rose curve.
    """
    # YOUR CODE HERE
    # Replace this with your color selection logic
    return PETAL_COLORS[0]  # Currently returns only the first color

# Draw the rose with colors
# TODO: Modify the drawing loop to use different colors per petal
for i in range(1, NUM_POINTS):
    x1, y1 = int(x[i-1]), int(y[i-1])
    x2, y2 = int(x[i]), int(y[i])

    # Get the color for this segment
    color = get_petal_color(theta[i], K_PARAMETER)

    # Draw line segment
    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

# Save result
output_path = SCRIPT_DIR / 'colored_rose.png'
image.save(output_path)
