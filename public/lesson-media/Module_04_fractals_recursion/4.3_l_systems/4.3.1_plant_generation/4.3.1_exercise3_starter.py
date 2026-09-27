import math
from PIL import Image, ImageDraw

AXIOM = "X"
RULES = {
    # TODO 1: define the X and F rules above
}
ANGLE = 25
ITERATIONS = 5
STEP = 3

def apply_rules(axiom, rules, n):
    s = axiom
    for _ in range(n):
        s = "".join(rules.get(c, c) for c in s)
    return s

def draw_lsystem(s, angle_deg, step, size):
    img = Image.new("RGB", size, (10, 20, 30))
    draw = ImageDraw.Draw(img)
    x, y, angle = size[0] // 4, size[1] - 40, -math.pi / 2
    stack = []
    for c in s:
        # TODO 2: handle F, +, -, [, ] correctly
        # Remember: X is silent.
        pass
    return img

s = apply_rules(AXIOM, RULES, ITERATIONS)
draw_lsystem(s, ANGLE, STEP, (800, 600)).save("my_fern.png")
