import numpy as np
from PIL import Image

LEFT, UP, RIGHT, DOWN = range(4)

def turn_left(d):  return (d + 3) % 4
def turn_right(d): return (d + 1) % 4

def generate_dragon_sequence(initial_turn, depth):
    if depth == 0:
        return initial_turn
    previous = generate_dragon_sequence(initial_turn, depth - 1)
    inverted = ''.join('L' if c == 'R' else 'R' for c in previous[::-1])
    return previous + 'R' + inverted

# Depth 10 → 2047 turn instructions
sequence = generate_dragon_sequence('R', 10)
print(f"Sequence length: {len(sequence)}")

# Walk the turtle: draw a 3-pixel step, then turn ('F' = one final step)
canvas = np.zeros((600, 800, 3), dtype=np.uint8)
STEPS = {LEFT: (-3, 0), UP: (0, -3), RIGHT: (3, 0), DOWN: (0, 3)}
x, y, direction = 550, 180, UP
for turn in sequence + 'F':
    dx, dy = STEPS[direction]
    new_x, new_y = x + dx, y + dy
    if dx:   # horizontal step
        canvas[y, min(x, new_x):max(x, new_x)] = (100, 180, 255)
    else:    # vertical step
        canvas[min(y, new_y):max(y, new_y), x] = (100, 180, 255)
    x, y = new_x, new_y
    direction = turn_right(direction) if turn == 'R' else turn_left(direction)

Image.fromarray(canvas).save('dragon_curve.png')
