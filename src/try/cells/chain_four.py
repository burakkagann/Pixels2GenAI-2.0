photo = load_photo()
BLUE = [32, 40, 120]
PINK = [235, 80, 125]
YELLOW = [245, 200, 60]
PAPER = [246, 238, 222]

def colour_of(light):
    if light < 90:
        return BLUE
    if light < 150:
        return PINK
    if light < 200:
        return YELLOW
    return PAPER

show(paint(photo, colour_of), "your poster")
