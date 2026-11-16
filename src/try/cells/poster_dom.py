photo = load_photo()                   # the Berliner Dom: 300 x 480 pixels

# change these, then run again
DARK = 90                              # darker than this: blue ink
MID = 150                              # darker than this: pink
INK = [32, 40, 120]
TONE = [235, 80, 125]
PAPER = [246, 238, 222]

poster = screenprint(photo, DARK, MID, INK, TONE, PAPER)
show(photo, "before")
show(poster, f"DARK = {DARK}, MID = {MID}")
