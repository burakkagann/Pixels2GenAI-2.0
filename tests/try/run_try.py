"""
Offline test of the /try sample cells and their checks ("Print the Berliner Dom as a poster").
Runs each cell the way the browser's cell worker does (helpers, code, check), with real NumPy and Pillow.
Every check must pass its solution and reject every wrong answer; a failure exits with code 1.
Run: python tests/try/run_try.py      (or: npm run test:try)
Author: Pixels2GenAI Project
"""
import contextlib
import io
import pathlib
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
CELLS = ROOT / "src" / "try" / "cells"
MEDIA = ROOT / "public" / "try-media"
HELPERS = (MEDIA / "helpers.py").read_text(encoding="utf-8")

# cell -> (solution as line swaps, [wrong answers as line swaps])
FIX_OLD = """    if light < 150:
        return PINK
    if light < 90:
        return BLUE                     # this never shows: why?"""
FIX_NEW = """    if light < 90:
        return BLUE
    if light < 150:
        return PINK"""
FIX_NO_BLUE = """    if light < 150:
        return PINK
    return PAPER"""
CASES = {
    "poster_dom.py": ([], []),
    "step1_compare.py": (
        [("THRESHOLD = 100", "THRESHOLD = 150")],
        [[], [("THRESHOLD = 100", "THRESHOLD = 220")], [("THRESHOLD = 100", "THRESHOLD = 20")],
         [("THRESHOLD = 100", "THRESHOLD = 120")], [("THRESHOLD = 100", "THRESHOLD = 201")]],
    ),
    "step2_rule.py": (
        [("if ___:", "if light < THRESHOLD:")],
        [[], [("if ___:", "if light > THRESHOLD:")], [("if ___:", "if light < 20:")], [("if ___:", "if light == THRESHOLD:")],
         [("if ___:", "if light < 130:")], [("if ___:", "if light < 120:")]],
    ),
    "step3_fix.py": (
        [(FIX_OLD, FIX_NEW)],
        [[], [("light < 90", "light < 60")], [(FIX_OLD, FIX_NEW), ("light < 150", "light < 120")],
         [(FIX_OLD, FIX_NO_BLUE)],
         [(FIX_OLD, FIX_NEW), ("light < 90", "light < 100")]],
    ),
}


def run(cell, swaps):
    code = (CELLS / cell).read_text(encoding="utf-8")
    for old, new in swaps:
        assert old in code, (cell, old)
        code = code.replace(old, new)
    images = []

    def show(img, caption=""):
        images.append((np.clip(np.asarray(img), 0, 255).astype(np.uint8), caption))

    ns = {"show": show, "_P2G_MEDIA_ROOT": str(MEDIA)}
    exec(HELPERS, ns)
    exec("import numpy as np", ns)
    out = io.StringIO()
    started = time.time()
    try:
        with contextlib.redirect_stdout(out):
            exec(code, ns)
    except Exception as error:  # a wrong answer may crash: that is the error box, not a check
        return None, f"ERROR {type(error).__name__}: {error}", images, time.time() - started
    verdict = None
    check_file = CELLS / cell.replace(".py", ".check.py")
    if check_file.exists():
        exec(check_file.read_text(encoding="utf-8"), ns)
        verdict = ns["check"]()
    return verdict, None, images, time.time() - started


failures = 0
for cell, (solution, wrongs) in CASES.items():
    has_check = (CELLS / cell.replace(".py", ".check.py")).exists()
    verdict, error, images, secs = run(cell, solution)
    ok = error is None and images and (verdict is None or verdict[0]) and (verdict is not None) == has_check
    failures += not ok
    print(f"{cell}: solution {'OK' if ok else 'FAIL'} ({secs:.2f}s) {error or ''} {verdict[1] if verdict else ''}")
    for wrong in wrongs:
        verdict, error, *_ = run(cell, wrong)
        rejected = error is not None or (verdict is not None and not verdict[0])
        failures += not rejected
        message = error or (verdict[1][-1] if verdict and not verdict[0] else verdict)
        print(f"   wrong {(wrong[-1][1] if wrong else 'starter code')!r}: {'rejected' if rejected else 'ACCEPTED (bad)'}: {message}")
print("failures:", failures)
sys.exit(1 if failures else 0)
