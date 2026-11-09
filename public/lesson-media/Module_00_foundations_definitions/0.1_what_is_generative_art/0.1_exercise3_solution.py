"""
Radial Scatter: the finished rule-based circle system.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image, ImageDraw

# ========== CONFIG: experiment after the TODOs are done ==========
WEDGES = 8     # Slices of the canvas, like a pie
SEED = 21      # Change it to let the same rules make another picture
# =================================================================

CANVAS = 800
CENTRE = CANVAS / 2
wedge_width = 2 * np.pi / WEDGES    # A full circle is 2 pi radians
random_numbers = np.random.default_rng(SEED)

image = Image.new("RGB", (CANVAS, CANVAS), "white")
draw = ImageDraw.Draw(image)

for wedge in range(WEDGES):
    # One colour per wedge: this rule gives the picture its structure.
    colour = tuple(int(value) for value in random_numbers.integers(40, 220, 3))

    # high is left out, so 11 gives whole numbers from 5 to 10.
    circle_count = random_numbers.integers(5, 11)

    for circle in range(circle_count):
        angle = (wedge + random_numbers.random()) * wedge_width
        distance = random_numbers.uniform(60, 340)

        # Given: turn the angle and distance into a position on the canvas.
        x = CENTRE + distance * np.cos(angle)
        y = CENTRE + distance * np.sin(angle)

        radius = random_numbers.uniform(10, 40)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                     fill=colour, outline="white")

image.save("radial_scatter.png")
print("Saved radial_scatter.png")
