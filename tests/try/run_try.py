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
import re
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


# ---- Go further: one code across the screens (GFC-1 b, 19 Nov 2026) ----
# The learner's step 3 answer, then each task's edit, must land on the next stage file; every stage runs on top of the last,
# starts at the previous stage's picture and ends at its own. Stage files: step 3 fixed, then four colours, grain, any number.
MDX = (ROOT / "src" / "try" / "print-the-berliner-dom.mdx").read_text(encoding="utf-8")
STAGE_COLOURS = {"chain_step3.py": 3, "chain_four.py": 4, "chain_grain.py": 4, "chain_bands.py": 5}


def stage(name):
    return (CELLS / name).read_text(encoding="utf-8").rstrip()


def last_picture(code):
    """Run code like the page does (helpers + show) and return (error, last image)."""
    _, error, images, _ = run_code(code)
    return error, (images[-1][0] if images else None)


def count_colours(picture):
    return len(np.unique(picture.reshape(-1, 3), axis=0))


def run_code(code):
    images = []
    ns = {"show": lambda img, caption="": images.append((np.clip(np.asarray(img), 0, 255).astype(np.uint8), caption)), "_P2G_MEDIA_ROOT": str(MEDIA)}
    exec(HELPERS, ns)
    exec("import numpy as np", ns)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, ns)
    except Exception as error:
        return None, f"ERROR {type(error).__name__}: {error}", images, 0
    return None, None, images, 0


def check_chain():
    bad = []
    # 1. step 3 solved by the learner (the swap the check wants) is exactly the code task 1 starts from
    step3_start = stage("step3_fix.py")
    solved = step3_start.replace(FIX_OLD, FIX_NEW)
    if solved != stage("chain_step3.py"):
        bad.append("step 3's solved code differs from chain_step3.py")
    # 2. the Go further cells in the lesson: same file name, one chain, each source is the stage before, each solution the next
    cells = re.findall(r'<Cell [^>]*>', MDX)
    chain = [c for c in cells if 'chain="poster"' in c]
    sources = [re.search(r'source="([^"]+)"', c) for c in chain]
    solutions = [re.search(r'solution="([^"]+)"', c).group(1) for c in chain]
    expected = ["chain_step3.py", "chain_four.py", "chain_grain.py", "chain_bands.py"]
    if solutions != expected:
        bad.append(f"chain solutions {solutions}, want {expected}")
    for i in range(1, len(chain)):
        if not sources[i] or sources[i].group(1) != solutions[i - 1]:
            bad.append(f"task {i} does not start from the solution before it ({sources[i].group(1) if sources[i] else None})")
        if 'file="my_poster.py"' not in chain[i]:
            bad.append(f"task {i} is not on my_poster.py")
    # 3. every stage runs on top of the last: it runs, starts from the previous stage's picture, ends at its own colour count
    previous = None
    for name in expected:
        error, picture = last_picture(stage(name))
        count = None if picture is None else count_colours(picture)
        ok = error is None and count == STAGE_COLOURS[name]
        print(f"chain {name}: {'OK' if ok else 'FAIL'} ({count} colours) {error or ''}")
        if not ok:
            bad.append(f"{name} gives {count} colours (want {STAGE_COLOURS[name]}) {error or ''}")
        # the stage keeps every line of the one before, unless a task replaces it (new lines are what the Solution marks)
        if previous is not None:
            kept = [line for line in previous.splitlines() if line.strip() and line in stage(name).splitlines()]
            print(f"   keeps {len(kept)} of {len([l for l in previous.splitlines() if l.strip()])} lines of the stage before")
            if len(kept) < 8:
                bad.append(f"{name} keeps too little of the stage before")
        previous = stage(name)
    # 4. a learner who finishes task 3 with a four-colour list gets four colours; with PURPLE, five (the task's own steps)
    four_list = stage("chain_bands.py").replace("PURPLE = [120, 60, 140]" + chr(10), "").replace("COLOURS = [BLUE, PURPLE, PINK, YELLOW, PAPER]", "COLOURS = [BLUE, PINK, YELLOW, PAPER]")
    error, picture = last_picture(four_list)
    if error or count_colours(picture) != 4:
        bad.append(f"task 3 step 1-2 (four-colour list) gives {error or count_colours(picture)}")
    # 5. a broken task 1 (an if with no body) fails the way Python says, so the strip can offer the solution
    broken = stage("chain_four.py").replace("        return YELLOW" + chr(10), "")
    error, _ = last_picture(broken)
    if not error or "IndentationError" not in error and "SyntaxError" not in error:
        bad.append(f"the broken task 1 should fail with an indent error, got {error}")
    else:
        print(f"chain broken task 1: error as expected ({error})")
    return bad


problems = check_chain()
for problem in problems:
    print("CHAIN FAIL:", problem)
failures += len(problems)
print("failures:", failures)
sys.exit(1 if failures else 0)
