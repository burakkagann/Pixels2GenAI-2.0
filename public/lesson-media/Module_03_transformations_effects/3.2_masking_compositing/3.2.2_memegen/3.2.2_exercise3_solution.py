from PIL import Image, ImageDraw, ImageFont

base = Image.open('bridge.png').convert('RGBA')
overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
font = ImageFont.truetype('arial.ttf', 30)

# Translucent banner behind the caption
banner = (0, 370, base.size[0], 480)
draw.rectangle(banner, fill=(0, 0, 0, 160))

# Caption on top, solid white
draw.text((20, 385), 'All your dreams are on their way', fill='white', font=font)
draw.text((20, 425), '(Simon & Garfunkel)',              fill='white', font=font)

result = Image.alpha_composite(base, overlay).convert('RGB')
result.save('caption_with_banner.png')
