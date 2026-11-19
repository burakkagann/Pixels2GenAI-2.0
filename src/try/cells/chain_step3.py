photo = load_photo()
BLUE = [32, 40, 120]
PINK = [235, 80, 125]
PAPER = [246, 238, 222]

def colour_of(light):
    if light < 90:
        return BLUE
    if light < 150:
        return PINK
    return PAPER

show(paint(photo, colour_of), "your poster")
