def check():
    idea = "Dark pixels get blue: the rule is True when light is below THRESHOLD."
    line = "Line 7: if light < THRESHOLD:"
    tests = {0: BLUE, 50: BLUE, THRESHOLD - 1: BLUE, THRESHOLD: PAPER, 255: PAPER}
    got = {n: list(ink_or_paper(n)) for n in tests}
    if all(got[n] == list(c) for n, c in tests.items()):
        return True, "Stone in blue, sky on paper. One if coloured all 144,000 pixels."
    if all(got[n] == list(PAPER if c == BLUE else BLUE) for n, c in tests.items()):
        return False, [idea, "The wrong way round: the sky is blue and the stone is paper. Dark pixels have light below THRESHOLD.", line]
    return False, [idea, "Some dark pixels are not inked. Compare light with THRESHOLD.", line]
