
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
K_PARAMETER = 5      # Creates 5 petals (odd k)
AMPLITUDE = 180
NUM_POINTS = 1000

# Color palette for 5 petals - vibrant rainbow colors
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

def get_petal_color(theta_value, k):
    """
    Determine which petal color to use based on the angle.

    For a rose curve r = cos(k*theta) with odd k:
    - There are k petals
    - Each petal spans an angular range of 2*pi/k radians
    - We can determine which petal we're in by: int(theta * k / pi) % k

    Args:
        theta_value: Current angle in radians (0 to 2*pi)
        k: The k parameter of the rose curve

    Returns:
        tuple: RGB color for this position
    """
    # For odd k: the argument (k * theta) determines which petal
    # Each petal corresponds to one "lobe" of cos(k*theta)
    # The cos function completes k full cycles as theta goes from 0 to 2*pi
    # We map theta to petal index using the periodicity

    # Calculate which "half-period" of cos(k*theta) we're in
    # Each petal corresponds to the positive half of one cos cycle
    petal_index = int((theta_value * k / np.pi)) % k

    return PETAL_COLORS[petal_index % len(PETAL_COLORS)]

# Draw the rose with colors - each segment gets its color based on angle
for i in range(1, NUM_POINTS):
    x1, y1 = int(x[i-1]), int(y[i-1])
    x2, y2 = int(x[i]), int(y[i])

    # Get the color for this segment based on angle
    color = get_petal_color(theta[i], K_PARAMETER)

    # Draw line segment with the appropriate color
    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

# Save result
output_path = SCRIPT_DIR / 'colored_rose.png'
image.save(output_path)
