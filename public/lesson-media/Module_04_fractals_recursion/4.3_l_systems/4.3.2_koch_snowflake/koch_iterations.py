"""
koch_iterations.py — render the Koch snowflake at iterations 0 through 4
side by side, so the recursive "_/\\_" replacement is visible at every step.
The triangle slowly grows the characteristic six-pointed lacy boundary.

Pixels2GenAI Project
"""

import math
from PIL import Image, ImageDraw


PANEL_SIZE = 280
ANGLE_DEG = 60


def apply_rules(axiom, rules, iterations):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(c, c) for c in s)
    return s


def turtle_draw(instructions, step, angle_deg, start, start_angle, size, color):
    img = Image.new('RGB', size, (12, 14, 28))
    draw = ImageDraw.Draw(img)
    x, y = start
    angle = start_angle
    for c in instructions:
        if c == 'F':
            nx = x + step * math.cos(angle)
            ny = y + step * math.sin(angle)
            draw.line([(x, y), (nx, ny)], fill=color, width=2)
            x, y = nx, ny
        elif c == '+':
            angle -= math.radians(angle_deg)
        elif c == '-':
            angle += math.radians(angle_deg)
    return img


axiom = "F++F++F"
rules = {"F": "F-F++F-F"}

panels = []
for it in range(5):
    instructions = apply_rules(axiom, rules, it)
    side_pixels = 220  # fixed side length so all panels are the same scale
    step = side_pixels / (3 ** it)
    panel = turtle_draw(instructions, step, ANGLE_DEG,
                        start=(30, 100),
                        start_angle=0,
                        size=(PANEL_SIZE, PANEL_SIZE),
                        color=(220, 240, 255))
    # Add small iteration label
    ImageDraw.Draw(panel).text((10, 10), f"n={it}", fill=(180, 180, 200))
    panels.append(panel)

# Concatenate horizontally
total = Image.new('RGB', (PANEL_SIZE * len(panels), PANEL_SIZE), (12, 14, 28))
for i, p in enumerate(panels):
    total.paste(p, (i * PANEL_SIZE, 0))
total.save('koch_iterations.png')
print(f"Saved koch_iterations.png — iterations 0..4")
