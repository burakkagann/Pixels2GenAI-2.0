import math
from PIL import Image, ImageDraw

AXIOM = "X"
RULES = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
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
        if c == "F":
            nx = x + step * math.cos(angle); ny = y + step * math.sin(angle)
            draw.line([(x, y), (nx, ny)], fill=(80, 160, 80))
            x, y = nx, ny
        elif c == "+":   angle -= math.radians(angle_deg)
        elif c == "-":   angle += math.radians(angle_deg)
        elif c == "[":   stack.append((x, y, angle))
        elif c == "]":   x, y, angle = stack.pop()
    return img

s = apply_rules(AXIOM, RULES, ITERATIONS)
draw_lsystem(s, ANGLE, STEP, (800, 600)).save("my_fern.png")
