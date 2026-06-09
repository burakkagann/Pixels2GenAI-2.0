"""
koch_variants.py — render four Koch-family curves side by side: the classic
snowflake, the anti-snowflake (turn convention inverted), the quadratic
Koch curve (90-degree variant), and a Sierpinski arrowhead built with the
same axiom-and-rule framework. Each is one rule change away from the others
— a clean illustration that the L-system formalism subsumes the entire
family of geometric replacement fractals.

Pixels2GenAI Project
"""

import math
from PIL import Image, ImageDraw


PANEL_SIZE = 350


def apply_rules(axiom, rules, iterations):
    s = axiom
    for _ in range(iterations):
        s = "".join(rules.get(c, c) for c in s)
    return s


def turtle_draw(instructions, step, angle_deg, start, start_angle, size,
                color):
    img = Image.new('RGB', size, (12, 14, 28))
    draw = ImageDraw.Draw(img)
    x, y = start
    angle = start_angle
    for c in instructions:
        if c in ('F', 'G'):
            nx = x + step * math.cos(angle)
            ny = y + step * math.sin(angle)
            draw.line([(x, y), (nx, ny)], fill=color, width=2)
            x, y = nx, ny
        elif c == '+':
            angle -= math.radians(angle_deg)
        elif c == '-':
            angle += math.radians(angle_deg)
    return img


variants = [
    {
        'name': 'snowflake',
        'axiom': 'F++F++F',
        'rules': {'F': 'F-F++F-F'},
        'angle': 60, 'iters': 4,
        'side': 240, 'start': (40, 90), 'start_angle': 0,
        'color': (220, 240, 255),
    },
    {
        'name': 'anti-snow',
        'axiom': 'F++F++F',
        'rules': {'F': 'F+F--F+F'},
        'angle': 60, 'iters': 4,
        'side': 240, 'start': (40, 280), 'start_angle': 0,
        'color': (255, 200, 110),
    },
    {
        'name': 'quad',
        'axiom': 'F+F+F+F',
        'rules': {'F': 'F+F-F-F+F'},
        'angle': 90, 'iters': 3,
        'side': 200, 'start': (60, 60), 'start_angle': 0,
        'color': (160, 220, 255),
    },
    {
        'name': 'arrowhead',
        'axiom': 'A',
        'rules': {'A': 'B-A-B', 'B': 'A+B+A'},
        'angle': 60, 'iters': 6,
        'side': 280, 'start': (40, 280), 'start_angle': 0,
        'color': (200, 255, 200),
    },
]


def make_panel(cfg):
    instr = apply_rules(cfg['axiom'], cfg['rules'], cfg['iters'])
    # The Sierpinski arrowhead uses A and B both as draw commands; the
    # turtle_draw above handles 'F' and 'G' as draw. Map A->F, B->G.
    instr = instr.replace('A', 'F').replace('B', 'G')

    # For the quad variant the resulting curve forms a closed square — the
    # step needs to be scaled by 3^iters along each side.
    step = cfg['side'] / (3 ** cfg['iters']) if cfg['name'] != 'arrowhead' \
        else cfg['side'] / (2 ** cfg['iters'])

    return turtle_draw(instr, step, cfg['angle'], cfg['start'],
                       cfg['start_angle'],
                       (PANEL_SIZE, PANEL_SIZE), cfg['color'])


panels = [make_panel(cfg) for cfg in variants]

# Concatenate horizontally with thin separators
total = Image.new('RGB', (PANEL_SIZE * 4, PANEL_SIZE), (12, 14, 28))
for i, p in enumerate(panels):
    total.paste(p, (i * PANEL_SIZE, 0))
    ImageDraw.Draw(total).text((i * PANEL_SIZE + 10, 10),
                               variants[i]['name'],
                               fill=(220, 220, 230))
total.save('koch_variants.png')
print('Saved koch_variants.png — snowflake | anti | quad | arrowhead')
