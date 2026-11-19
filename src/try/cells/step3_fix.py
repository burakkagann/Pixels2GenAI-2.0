photo = load_photo()
BLUE = [32, 40, 120]
PINK = [235, 80, 125]
PAPER = [246, 238, 222]

def three_colours(light):
    if light < 150:
        return PINK
    if light < 90:
        return BLUE                     # this never shows: why?
    return PAPER

show(paint(photo, three_colours), "three colours?")
