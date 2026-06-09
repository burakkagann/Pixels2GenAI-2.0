

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Helper function to draw a circle on a canvas
# =============================================================================
def draw_circle(canvas, center_x, center_y, radius, color):
    """Draw a filled circle on the canvas using distance-based masking."""
    height, width = canvas.shape[:2]
    Y, X = np.ogrid[0:height, 0:width]
    square_dist = (X - center_x) ** 2 + (Y - center_y) ** 2
    mask = square_dist < radius ** 2
    canvas[mask] = color
    return canvas

# =============================================================================
# Create four different circle variations
# =============================================================================
SIZE = 256  # Each sub-image size

# Variation 1: Small radius
canvas1 = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
draw_circle(canvas1, 128, 128, 50, [255, 128, 0])  # Small orange

# Variation 2: Large radius
canvas2 = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
draw_circle(canvas2, 128, 128, 110, [255, 128, 0])  # Large orange

# Variation 3: Off-center position
canvas3 = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
draw_circle(canvas3, 80, 80, 70, [0, 150, 255])  # Blue, top-left

# Variation 4: Multiple circles
canvas4 = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
draw_circle(canvas4, 85, 128, 60, [255, 0, 100])    # Pink, left
draw_circle(canvas4, 171, 128, 60, [100, 255, 0])   # Green, right

# =============================================================================
# Create comparison grid with matplotlib
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(8, 8), dpi=150)

titles = [
    'Small Radius (r=50)',
    'Large Radius (r=110)',
    'Off-Center Position',
    'Multiple Circles'
]

canvases = [canvas1, canvas2, canvas3, canvas4]

for ax, canvas, title in zip(axes.flatten(), canvases, titles):
    ax.imshow(canvas)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.axis('off')

plt.suptitle('Circle Parameter Variations', fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('circle_variations.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
