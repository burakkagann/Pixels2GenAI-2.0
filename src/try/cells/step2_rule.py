photo = load_photo()
THRESHOLD = 110
BLUE = [32, 40, 120]
PAPER = [246, 238, 222]

def ink_or_paper(light):
    if ___:
        return BLUE
    return PAPER

poster = paint(photo, ink_or_paper)    # runs your rule on every pixel's brightness
show(poster, "your two-colour poster")
