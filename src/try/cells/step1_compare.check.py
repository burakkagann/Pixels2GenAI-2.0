def check():
    idea = "light < THRESHOLD is True for every number below the threshold."
    line = "Line 1: any THRESHOLD above 120 and up to 200, for example THRESHOLD = 150"
    inked = [n for n in [30, 200, 120, 90] if n < THRESHOLD]
    if len(inked) == 3:
        return True, f"30, 120 and 90 are below {THRESHOLD}: three squares of ink."
    if len(inked) < 3:
        return False, [idea, f"Only {len(inked)} below {THRESHOLD}. Raise it past 120.", line]
    return False, [idea, f"All four are below {THRESHOLD}. Keep it at 200 or less.", line]
