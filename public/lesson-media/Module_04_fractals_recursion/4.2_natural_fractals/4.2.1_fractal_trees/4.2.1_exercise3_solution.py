import math, random
from PIL import Image, ImageDraw

def draw_branch_organic(draw, x, y, length, angle, depth, branch_angle, length_ratio):
    if depth == 0 or length < 2:
        return
    if random.random() < 0.1:
        return

    angle += random.uniform(-0.15, 0.15)
    length_ratio = max(0.4, min(0.9, length_ratio + random.uniform(-0.1, 0.1)))

    end_x = x + length * math.sin(angle)
    end_y = y - length * math.cos(angle)
    draw.line([(x, y), (end_x, end_y)], fill=(101, 67, 33), width=max(1, depth // 2))

    new_length = length * length_ratio
    draw_branch_organic(draw, end_x, end_y, new_length,
                        angle - branch_angle, depth - 1, branch_angle, length_ratio)
    draw_branch_organic(draw, end_x, end_y, new_length,
                        angle + branch_angle, depth - 1, branch_angle, length_ratio)

random.seed(0)
img = Image.new('RGB', (512, 512), 'white')
draw_branch_organic(ImageDraw.Draw(img), 256, 462, 120, 0, 9, math.radians(25), 0.72)
img.save('natural_tree.png')
