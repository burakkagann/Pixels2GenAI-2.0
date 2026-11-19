def check():
    idea = "Python checks the ifs from the top and stops at the first True one. Which if must come first?"
    line = "Lines 7 to 10: check light < 90 first, then light < 150"
    want = {10: BLUE, 89: BLUE, 90: PINK, 100: PINK, 149: PINK, 150: PAPER, 200: PAPER}
    got = {n: list(three_colours(n)) for n in want}
    if all(got[n] == list(c) for n, c in want.items()):
        return True, "Blue below 90, pink from 90 to 149, paper from 150: three colours."
    if got[10] == list(PINK):
        return False, [idea, "A pixel at 10 is also below 150, so it stops at the first if and turns pink.", line]
    return False, [idea, "Keep the numbers 90 and 150; change only the order.", line]
