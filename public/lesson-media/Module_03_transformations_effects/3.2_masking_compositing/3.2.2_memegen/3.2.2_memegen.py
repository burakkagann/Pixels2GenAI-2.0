from PIL import Image, ImageDraw, ImageFont

img = Image.open('bridge.png')
draw = ImageDraw.Draw(img)
font = ImageFont.truetype('arial.ttf', 30)

draw.text((20, 390), 'All your dreams are on their way',
          fill='white', font=font)
draw.text((20, 430), '(Simon & Garfunkel)',
          fill='white', font=font)

img.save('bridge_meme.png')
