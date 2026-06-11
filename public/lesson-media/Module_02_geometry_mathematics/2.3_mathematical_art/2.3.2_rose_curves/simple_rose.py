import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# Canvas settings
CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
BACKGROUND_COLOR = (15, 15, 25)    # Dark blue-black
ROSE_COLOR = (255, 100, 150)       # Pink

# Rose curve parameters
K_PARAMETER = 5      # Number of petals (for odd k)
AMPLITUDE = 180      # Size of the rose (maximum radius)
NUM_POINTS = 1000    # Smoothness of the curve

# Create canvas
image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# Generate rose curve points using polar equation: r = a * cos(k * theta)
# For odd k: the curve traces k petals in one full rotation (0 to pi)
# We use 0 to 2*pi to ensure complete coverage
theta = np.linspace(0, 2 * np.pi, NUM_POINTS)
r = AMPLITUDE * np.cos(K_PARAMETER * theta)

# Convert polar coordinates to Cartesian coordinates
# x = r * cos(theta), y = r * sin(theta)
x = CENTER + r * np.cos(theta)
y = CENTER + r * np.sin(theta)

# Draw the rose by connecting consecutive points as a line
points = list(zip(x.astype(int), y.astype(int)))
draw.line(points, fill=ROSE_COLOR, width=2)

# Save result
output_path = SCRIPT_DIR / 'simple_rose.png'
image.save(output_path)
