"""
simple_koch.py — draw the Koch snowflake by L-system. The Koch curve has
axiom F++F++F (an equilateral triangle, as three forward segments separated
by 120-degree turns) and rule F -> F-F++F-F (each forward segment becomes a
"_/\\_" zigzag). Iterating the rule N times and walking the turtle yields
the canonical Koch snowflake.

Pixels2GenAI Project
"""

import math
from PIL import Image, ImageDraw


SIZE = (700, 600)
ANGLE_DEG = 60
ITERATIONS = 4


def apply_rules(axiom, rules, iterations):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(c, c) for c in s)
    return s


def turtle_draw(instructions, angle_deg, step, start, start_angle, size, color):
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
instructions = apply_rules(axiom, rules, ITERATIONS)

# Step size shrinks by 3^iterations so the snowflake stays bounded.
base_step = 400 / (3 ** ITERATIONS)

img = turtle_draw(instructions, ANGLE_DEG, base_step,
                  start=(150, 200), start_angle=0,
                  size=SIZE, color=(220, 240, 255))
img.save('simple_koch.png')
print(f"Saved simple_koch.png — iteration {ITERATIONS}, "
      f"{len(instructions)} symbols")
