photo = load_photo()
BLUE = [32, 40, 120]
PURPLE = [120, 60, 140]
PINK = [235, 80, 125]
YELLOW = [245, 200, 60]
PAPER = [246, 238, 222]
COLOURS = [BLUE, PURPLE, PINK, YELLOW, PAPER]

def colour_of(light):
    band = int(light * len(COLOURS) / 256)
    return COLOURS[band]

GRAIN = 20                              # try 0, 40, 80
rng = np.random.default_rng(1)
noise = rng.integers(-GRAIN, GRAIN + 1, (300, 480, 1))
grainy = np.clip(photo + noise, 0, 255)

show(paint(grainy, colour_of), "your poster")
