import numpy as np
from PIL import Image, ImageDraw
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

# =============================================================================
# Configuration: Harmonograph parameters (try changing these!)
# =============================================================================
CANVAS_SIZE = 512
CENTER = CANVAS_SIZE // 2
BACKGROUND_COLOR = (10, 10, 20)      # Deep navy background
LINE_COLOR = (100, 200, 255)         # Cyan blue line

# Pendulum X parameters (controls horizontal motion)
FREQ_X = 3              # Frequency of x oscillation
AMP_X = 200             # Amplitude (maximum displacement) in x
PHASE_X = 0             # Starting phase angle for x pendulum

# Pendulum Y parameters (controls vertical motion)
FREQ_Y = 2              # Frequency of y oscillation
AMP_Y = 200             # Amplitude (maximum displacement) in y
PHASE_Y = np.pi / 2     # Starting phase angle for y pendulum (90 degrees)

# Damping and time parameters
DAMPING = 0.002         # How quickly the oscillation decays (higher = faster decay)
NUM_POINTS = 5000       # Number of points to trace (more = smoother curve)

# =============================================================================
# Step 1: Create time array (represents pendulum swing duration)
# =============================================================================
# Time goes from 0 to a large value to allow the pattern to fully develop
t = np.linspace(0, 100, NUM_POINTS)

# =============================================================================
# Step 2: Calculate damped oscillation for each axis
# =============================================================================
# Harmonograph equations with exponential damping:
# x(t) = A_x * sin(f_x * t + p_x) * e^(-d * t)
# y(t) = A_y * sin(f_y * t + p_y) * e^(-d * t)

# The damping factor causes amplitude to decrease over time
decay = np.exp(-DAMPING * t)

# Calculate x and y positions at each time step
x = AMP_X * np.sin(FREQ_X * t + PHASE_X) * decay
y = AMP_Y * np.sin(FREQ_Y * t + PHASE_Y) * decay

# =============================================================================
# Step 3: Convert to canvas coordinates (centered on canvas)
# =============================================================================
canvas_x = CENTER + x
canvas_y = CENTER + y

# =============================================================================
# Step 4: Create canvas and draw the harmonograph curve
# =============================================================================
image = Image.new('RGB', (CANVAS_SIZE, CANVAS_SIZE), BACKGROUND_COLOR)
draw = ImageDraw.Draw(image)

# Convert to integer coordinates and draw as connected line
points = list(zip(canvas_x.astype(int), canvas_y.astype(int)))
draw.line(points, fill=LINE_COLOR, width=1)

# =============================================================================
# Step 5: Save the result
# =============================================================================
output_path = SCRIPT_DIR / 'simple_harmonograph.png'
image.save(output_path)
