THRESHOLD = 100

for light in [30, 200, 120, 90]:
    print(light, light < THRESHOLD)    # predict: which say True?

show(grey_swatches([30, 200, 120, 90]), "four pixels")
show(ink_swatches([30, 200, 120, 90], THRESHOLD), "ink where True")
