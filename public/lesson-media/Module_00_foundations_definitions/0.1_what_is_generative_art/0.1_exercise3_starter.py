"""
Radial Scatter: a rule-based circle system. Fill in the TODOs to finish the rules.

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

    # TODO 1: Pick how many circles this wedge gets: a whole number from 5 to 10.
    # Why: the count varies, so no two pictures have the same rhythm.
    # Use random_numbers.integers(low, high), which leaves out high.
    circle_count = 1

    for circle in range(circle_count):
        # TODO 2: Pick an angle inside this wedge.
        # Why: circles stay in their slice. This is where order lives.
        # The wedge starts at wedge * wedge_width. Add a random part of wedge_width.
        angle = 0.0

        # TODO 3: Pick a distance from the centre, from 60 to 340 pixels.
        # Why: this is where disorder lives. Use random_numbers.uniform(low, high).
        distance = 0.0

        # Given: turn the angle and distance into a position on the canvas.
        x = CENTRE + distance * np.cos(angle)
        y = CENTRE + distance * np.sin(angle)

        # TODO 4: Pick a radius from 10 to 40 pixels.
        # Why: size carries the variation you see first.
        radius = 1.0

        # TODO 5: Draw the circle with draw.ellipse.
        # It takes the box around the circle: [left, top, right, bottom].
        # Why: nothing appears until this runs. fill=colour and outline="white"
        # keep overlapping circles readable.
        pass

image.save("radial_scatter.png")
print("Saved radial_scatter.png")
