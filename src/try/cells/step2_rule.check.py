def check():
    idea = "Dark pixels get ink: the rule is True when light is below THRESHOLD."
    line = "Line 7: if light < THRESHOLD:"
    tests = {0: INK, 50: INK, THRESHOLD - 1: INK, THRESHOLD: PAPER, 255: PAPER}
    got = {n: list(ink_or_paper(n)) for n in tests}
    if all(got[n] == list(c) for n, c in tests.items()):
        return True, "Stone in ink, sky on paper: one if, 144,000 pixels."
    if all(got[n] == list(PAPER if c == INK else INK) for n, c in tests.items()):
        return False, [idea, "Turned around: the sky is inked and the stone is paper. Flip the comparison.", line]
    return False, [idea, "Some dark pixels are not inked. Compare light with THRESHOLD.", line]
