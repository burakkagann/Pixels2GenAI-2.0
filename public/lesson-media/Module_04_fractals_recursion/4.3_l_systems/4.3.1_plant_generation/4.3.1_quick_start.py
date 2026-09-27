import math
from PIL import Image, ImageDraw

AXIOM = "F"
RULES = {"F": "F[+F]F[-F]F"}
ITERATIONS = 4
ANGLE = 25.7

# Apply rules ITERATIONS times — every F becomes the rule's expansion
s = AXIOM
for _ in range(ITERATIONS):
    s = "".join(RULES.get(c, c) for c in s)

# Turtle interpretation
img = Image.new("RGB", (800, 600), (10, 20, 30))
draw = ImageDraw.Draw(img)
x, y, angle = 400, 550, -math.pi / 2          # start centre-bottom, facing up
stack = []
step = 5

for symbol in s:
    if symbol == "F":
        nx = x + step * math.cos(angle)
        ny = y + step * math.sin(angle)
        draw.line([(x, y), (nx, ny)], fill=(100, 180, 100))
        x, y = nx, ny
    elif symbol == "+": angle -= math.radians(ANGLE)
    elif symbol == "-": angle += math.radians(ANGLE)
    elif symbol == "[": stack.append((x, y, angle))
    elif symbol == "]": x, y, angle = stack.pop()

img.save("plant_basic.png")
