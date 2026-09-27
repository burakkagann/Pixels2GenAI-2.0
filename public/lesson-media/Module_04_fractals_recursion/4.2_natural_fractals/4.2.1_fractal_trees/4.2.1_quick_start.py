import math
from PIL import Image, ImageDraw

def draw_branch(draw, x, y, length, angle, depth):
    if depth == 0:
        return
    ex = x + length * math.sin(angle)
    ey = y - length * math.cos(angle)            # subtract: image y points down
    draw.line([(x, y), (ex, ey)], fill=(101, 67, 33), width=max(1, depth // 2))

    new_length = length * 0.7
    draw_branch(draw, ex, ey, new_length, angle - math.radians(25), depth - 1)
    draw_branch(draw, ex, ey, new_length, angle + math.radians(25), depth - 1)

img = Image.new('RGB', (512, 512), 'white')
draw_branch(ImageDraw.Draw(img), 256, 462, 120, 0, 8)
img.save('fractal_tree.png')
