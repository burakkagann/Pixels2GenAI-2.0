photo = load_photo()
INK = [32, 40, 120]
TONE = [235, 80, 125]
PAPER = [246, 238, 222]

def three_tones(light):
    if light < 150:
        return TONE
    if light < 90:
        return INK                     # this never shows: why?
    return PAPER

show(paint(photo, three_tones), "three tones?")
