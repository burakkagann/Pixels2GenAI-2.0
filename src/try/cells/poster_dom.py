photo = load_photo()                   # the Berliner Dom: 300 x 480 pixels

# change these, then run again
DARK = 90                              # darker than this: blue
MID = 150                              # darker than this: pink
BLUE = [32, 40, 120]               # each colour as red, green, blue
PINK = [235, 80, 125]
PAPER = [246, 238, 222]

poster = screenprint(photo, DARK, MID, BLUE, PINK, PAPER)
show(photo, "before")
show(poster, f"DARK = {DARK}, MID = {MID}")
