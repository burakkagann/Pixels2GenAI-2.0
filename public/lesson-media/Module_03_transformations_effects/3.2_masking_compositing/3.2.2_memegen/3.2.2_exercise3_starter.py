from PIL import Image, ImageDraw, ImageFont

# Open as RGBA so the overlay can be transparent
base = Image.open('bridge.png').convert('RGBA')
overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))   # fully transparent

draw = ImageDraw.Draw(overlay)
font = ImageFont.truetype('arial.ttf', 30)

# TODO 1: draw a half-transparent black rectangle behind the caption area.
#         draw.rectangle((x0, y0, x1, y1), fill=(0, 0, 0, alpha))

# TODO 2: draw the two-line caption *on the overlay*, in solid white.

# TODO 3: alpha-composite the overlay onto the base, then save.
result = Image.alpha_composite(base, overlay).convert('RGB')
result.save('caption_with_banner.png')
