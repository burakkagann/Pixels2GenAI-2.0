"""
Runner check (Milestone 1b): does lesson code really run in the browser?

Part 1, UI test: opens a Module 3 lesson, clicks Run on the quick start, and checks
        that an output image appears; also checks that a Module 4 lesson (out of
        scope) shows no Run button.
Part 2, script check: runs every downloadable .py of Modules 1-6 and 8 through the
        SAME worker the site uses (public/runner/python-worker.mjs), in headless
        Chromium, and records success, error and run time.

Needs the dev server:  npm run dev   (http://localhost:4321)
Run from the repo root:
    ai-tutor/.venv/Scripts/python ai-tutor/evals/runner_check.py            # both parts
    ai-tutor/.venv/Scripts/python ai-tutor/evals/runner_check.py --ui-only
Writes ai-tutor/evals/results/runner_check.md and runner_check.json.

Author: Pixels2GenAI Project
"""

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = REPO_ROOT / "public" / "lesson-media"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
BASE_URL = "http://localhost:4321"
MODULES = ("Module_01", "Module_02", "Module_03", "Module_04", "Module_05", "Module_06", "Module_08")
SCRIPT_TIMEOUT_MS = 90_000
FIRST_LOAD_TIMEOUT_MS = 180_000   # the very first run also downloads Pyodide and packages

# Starter and template files have TODO gaps on purpose; they are reported separately.
INCOMPLETE_MARKERS = ("starter", "template")
# Exercise files that leave gaps as `...` for the learner (e.g. `color = ...`) are
# incomplete by design too, whatever their name.
PLACEHOLDER = re.compile(r"(=|\(|,)\s*\.\.\.\s*(#|\)|,|$)", re.MULTILINE)

# Runs inside the page: one worker, recreated if a script times out (the only way to
# stop a runaway Python loop), exactly as the site's Run button does.
PAGE_HELPER = """
window.__runScript = (code, assetBase, fileName, timeoutMs) => new Promise((resolve) => {
  if (!window.__worker) {
    window.__worker = new Worker('/runner/python-worker.mjs', { type: 'module' });
    window.__worker.onmessage = ({ data }) => window.__resolve && window.__resolve(data);
  }
  const started = performance.now();
  const timer = setTimeout(() => {
    window.__worker.terminate();
    window.__worker = null;
    resolve({ ok: false, timedOut: true, error: 'timeout', images: [], timings: {} });
  }, timeoutMs);
  window.__resolve = (data) => {
    clearTimeout(timer);
    resolve({ ok: data.ok, error: data.error || '', stderr: data.stderr || '',
              images: (data.images || []).map((i) => i.name), inputs: data.inputs || [],
              timings: data.timings || {}, wallMs: Math.round(performance.now() - started) });
  };
  window.__worker.postMessage({ id: Date.now(), code, assetBase, fileName });
});
"""


def ui_test(page):
    """End-to-end: the real button on the real lesson page."""
    results = {}
    page.goto(f"{BASE_URL}/lessons/3.2.1", wait_until="networkidle")
    run_buttons = page.locator(".code .chrome .run")
    results["run_buttons_on_3.2.1"] = run_buttons.count()
    run_buttons.first.click()
    # The first run downloads Pyodide + numpy + Pillow; allow for a slow connection.
    page.wait_for_selector(".code-output img, .code-output-status:text('error')", timeout=FIRST_LOAD_TIMEOUT_MS)
    output = page.locator(".code-output").first
    results["status"] = output.locator(".code-output-status").inner_text()
    results["images_shown"] = output.locator("img").count()
    RESULTS_DIR.mkdir(exist_ok=True)
    output.screenshot(path=str(RESULTS_DIR / "runner_ui_3.2.1.png"))

    page.goto(f"{BASE_URL}/lessons/4.1.1", wait_until="networkidle")
    results["run_buttons_on_4.1.1"] = page.locator(".code .chrome .run").count()
    results["passed"] = (results["run_buttons_on_3.2.1"] > 0 and results["images_shown"] > 0
                         and results["run_buttons_on_4.1.1"] == 0)
    return results


def script_check(page):
    """Every Module 1-6/8 script through the site's worker."""
    page.goto(f"{BASE_URL}/lessons/1.1.1", wait_until="networkidle")
    page.evaluate(PAGE_HELPER)
    scripts = sorted(path for path in MEDIA_DIR.rglob("*.py") if path.relative_to(MEDIA_DIR).parts[0][:9] in MODULES)
    records = []
    for number, path in enumerate(scripts, start=1):
        relative = path.relative_to(MEDIA_DIR).as_posix()
        asset_base = "/lesson-media/" + relative.rsplit("/", 1)[0] + "/"
        timeout = FIRST_LOAD_TIMEOUT_MS if number == 1 else SCRIPT_TIMEOUT_MS
        code = path.read_text(encoding="utf-8", errors="replace")
        result = page.evaluate("([c, b, f, t]) => window.__runScript(c, b, f, t)", [code, asset_base, path.name, timeout])
        error_lines = [line for line in (result.get("error") or "").strip().splitlines() if line.strip()]
        record = {
            "script": relative,
            "module": relative[:9],
            "incomplete_by_design": (any(marker in path.stem.lower() for marker in INCOMPLETE_MARKERS)
                                     or bool(PLACEHOLDER.search(code))),
            "ok": result["ok"],
            "timed_out": result.get("timedOut", False),
            "error": error_lines[-1][:200] if error_lines else "",
            "images": result.get("images", []),
            "run_ms": result.get("timings", {}).get("runMs"),
            "wall_ms": result.get("wallMs"),
        }
        records.append(record)
        mark = "ok " if record["ok"] else ("TIMEOUT" if record["timed_out"] else "FAIL")
        print(f"[{number:3}/{len(scripts)}] {mark:7} {relative}  {record['error'][:80]}", flush=True)
    return records


def write_report(ui, records):
    lines = ["# Runner check (in-browser Python, Milestone 1b)", "",
             f"Date: {time.strftime('%Y-%m-%d')}. Pyodide 314.0.7 in headless Chromium, through public/runner/python-worker.mjs.", ""]
    if ui:
        lines += ["## UI test", "",
                  f"- Run buttons on 3.2.1 (Module 3): {ui['run_buttons_on_3.2.1']}",
                  f"- After clicking Run: \"{ui['status']}\", {ui['images_shown']} output image(s) shown",
                  f"- Run buttons on 4.1.1 (Module 4, out of scope): {ui['run_buttons_on_4.1.1']}",
                  f"- **Result: {'passed' if ui['passed'] else 'FAILED'}** (screenshot: runner_ui_3.2.1.png)", ""]
    if records:
        complete = [r for r in records if not r["incomplete_by_design"]]
        passed = [r for r in complete if r["ok"]]
        run_times = sorted(r["run_ms"] for r in passed if r["run_ms"] is not None)
        lines += ["## Script check", "",
                  f"- Complete scripts (not starters/templates): **{len(passed)} of {len(complete)} ran successfully "
                  f"({len(passed) / len(complete):.0%})**",
                  f"- Starter/template files (expected to stop at their TODOs): {len(records) - len(complete)}, "
                  f"of which {sum(r['ok'] for r in records if r['incomplete_by_design'])} ran anyway",
                  f"- Run time of successful scripts: median {run_times[len(run_times) // 2] / 1000:.1f} s, "
                  f"slowest {run_times[-1] / 1000:.1f} s" if run_times else "- no successful runs",
                  "", "| Module | Complete scripts | Ran | Share |", "|---|---|---|---|"]
        for module in MODULES:
            in_module = [r for r in complete if r["module"] == module]
            if in_module:
                ok = sum(r["ok"] for r in in_module)
                lines.append(f"| {module} | {len(in_module)} | {ok} | {ok / len(in_module):.0%} |")
        slowest = sorted((r for r in passed if r["run_ms"]), key=lambda r: -r["run_ms"])[:5]
        lines += ["", "### Slowest successful scripts", "", "| Script | Run time |", "|---|---|"]
        lines += [f"| `{r['script']}` | {r['run_ms'] / 1000:.1f} s |" for r in slowest]
        failures = [r for r in complete if not r["ok"]]
        if failures:
            lines += ["", "### Failures (complete scripts)", "", "| Script | Error (last line) |", "|---|---|"]
            lines += [f"| `{r['script']}` | {'timeout' if r['timed_out'] else r['error'].replace('|', '/')} |" for r in failures]
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "runner_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (RESULTS_DIR / "runner_check.json").write_text(json.dumps({"ui": ui, "scripts": records}, indent=2), encoding="utf-8")
    print("\n".join(lines))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ui_only = "--ui-only" in sys.argv
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        ui = ui_test(page)
        print("UI test:", json.dumps(ui), flush=True)
        records = [] if ui_only else script_check(page)
        browser.close()
    write_report(ui, records)


if __name__ == "__main__":
    main()
