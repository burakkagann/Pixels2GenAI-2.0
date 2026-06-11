
import numpy as np
from PIL import Image

# Configuration
PANEL_SIZE = 400        # Size of each panel
NUM_STARS = 200         # Same number of stars in each panel
BACKGROUND = 0          # Black background

# Create two panels side by side (800 x 400)
comparison = np.full((PANEL_SIZE, PANEL_SIZE * 2), BACKGROUND, dtype=np.uint8)

# === LEFT PANEL: Uniform Distribution ===
# Stars are equally likely to appear anywhere
x_uniform = np.random.randint(0, PANEL_SIZE, size=NUM_STARS)
y_uniform = np.random.randint(0, PANEL_SIZE, size=NUM_STARS)
comparison[y_uniform, x_uniform] = 255

# === RIGHT PANEL: Gaussian Distribution ===
# Stars cluster around the center with bell-curve falloff
CENTER = PANEL_SIZE // 2
SPREAD = 60  # Standard deviation

x_gaussian = np.random.normal(CENTER, SPREAD, size=NUM_STARS)
y_gaussian = np.random.normal(CENTER, SPREAD, size=NUM_STARS)

# Clip to panel bounds and shift to right panel (add PANEL_SIZE to x)
x_gaussian = np.clip(x_gaussian, 0, PANEL_SIZE - 1).astype(int) + PANEL_SIZE
y_gaussian = np.clip(y_gaussian, 0, PANEL_SIZE - 1).astype(int)

comparison[y_gaussian, x_gaussian] = 255

# Add a vertical divider line between panels
comparison[:, PANEL_SIZE - 1:PANEL_SIZE + 1] = 80  # Gray divider

# Save the comparison image
image = Image.fromarray(comparison, mode='L')
image.save('distribution_comparison.png')
