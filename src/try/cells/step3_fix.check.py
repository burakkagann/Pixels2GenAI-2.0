def check():
    idea = "Python checks the ifs from the top and stops at the first True one."
    line = "Lines 7 to 10: check light < 90 first, then light < 150"
    want = {10: INK, 89: INK, 90: TONE, 100: TONE, 149: TONE, 150: PAPER, 200: PAPER}
    got = {n: list(three_tones(n)) for n in want}
    if all(got[n] == list(c) for n, c in want.items()):
        return True, "Blue below 90, pink to 150, paper above: three tones."
    if got[10] == list(TONE):
        return False, [idea, "A pixel at 10 is also below 150, so it stops at the first if and turns pink.", line]
    return False, [idea, "Keep the numbers 90 and 150; change only the order.", line]
