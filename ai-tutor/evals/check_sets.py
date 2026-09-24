"""
Helper for writing eval questions.

List the sections (gold ids) of a lesson, to copy into a question's "gold":
    python ai-tutor/evals/check_sets.py --list 3.2.1

Check every question file for mistakes (bad JSON, unknown gold ids, wrong kind):
    python ai-tutor/evals/check_sets.py

Needs ai-tutor/data/chunks.json: run python ai-tutor/chunker.py first.

Author: Pixels2GenAI Project
"""

import json
import sys
from collections import Counter
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
CHUNKS_FILE = EVALS_DIR.parent / "data" / "chunks.json"
VALID_KINDS = {"on_page", "off_page", "unanswerable"}
VALID_STYLES = {"everyday", "identifier", "curriculum_specific"}


def load_chunks():
    if not CHUNKS_FILE.exists():
        sys.exit("chunks.json not found: run  python ai-tutor/chunker.py  first.")
    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def list_sections(chunks, lesson_id):
    """Print every chunk id of one lesson with its title and first words."""
    lesson_chunks = [chunk for chunk in chunks if chunk["lesson_id"] == lesson_id]
    if not lesson_chunks:
        sys.exit(f"No chunks for lesson {lesson_id}. Is it shipped?")
    print(f"{lesson_id}  {lesson_chunks[0]['lesson_title']}\n")
    for chunk in lesson_chunks:
        preview = " ".join(chunk["text"].split())[:90]
        print(f'"{chunk["id"]}"')
        print(f"    {chunk['title']}  |  {preview}...\n")


def check_file(path, chunk_ids, lesson_ids):
    """Return a list of problems found in one question file."""
    problems = []
    seen_ids = Counter()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        where = f"{path.name} line {line_number}"
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            # The most common cause: a missing comma or quote, or a trailing comma.
            problems.append(f"{where}: not valid JSON ({error.msg} at column {error.colno})")
            continue
        seen_ids[row.get("id")] += 1
        for field in ("id", "asked_on", "question", "gold"):
            if field not in row:
                problems.append(f"{where}: missing field '{field}'")
        if row.get("asked_on") not in lesson_ids:
            problems.append(f"{where}: asked_on '{row.get('asked_on')}' is not a shipped lesson")
        for gold_id in row.get("gold", []) + row.get("closest", []):
            if gold_id not in chunk_ids:
                problems.append(f"{where}: gold '{gold_id}' is not a chunk id (use --list to copy one)")
        kind = row.get("kind")
        if kind is not None and kind not in VALID_KINDS:
            problems.append(f"{where}: kind '{kind}' should be one of {sorted(VALID_KINDS)}")
        style = row.get("style")
        if style is not None and style not in VALID_STYLES:
            problems.append(f"{where}: style '{style}' should be one of {sorted(VALID_STYLES)}")
        if row.get("split") not in (None, "dev", "test"):
            problems.append(f"{where}: split '{row.get('split')}' should be 'dev' or 'test'")
        gold_lessons = {gold_id.split("#")[0] for gold_id in row.get("gold", [])}
        if kind == "on_page" and row.get("asked_on") not in gold_lessons:
            problems.append(f"{where}: kind is on_page but no gold answer is on {row.get('asked_on')}")
        if kind == "off_page" and row.get("asked_on") in gold_lessons:
            problems.append(f"{where}: kind is off_page but a gold answer is on the same page")
        if kind == "unanswerable" and row.get("gold"):
            problems.append(f"{where}: unanswerable questions must have an empty gold list")
    for question_id, count in seen_ids.items():
        if count > 1:
            problems.append(f"{path.name}: id '{question_id}' is used {count} times")
    return problems


def main():
    # Lesson titles contain characters like '—' that the Windows console's default
    # code page cannot print; switch this script's output to UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    chunks = load_chunks()
    if len(sys.argv) == 3 and sys.argv[1] == "--list":
        list_sections(chunks, sys.argv[2])
        return

    chunk_ids = {chunk["id"] for chunk in chunks}
    lesson_ids = {chunk["lesson_id"] for chunk in chunks}
    all_problems = []
    for path in sorted(EVALS_DIR.glob("*.jsonl")):
        problems = check_file(path, chunk_ids, lesson_ids)
        rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        print(f"{path.name}: {len(rows)} questions, {len(problems)} problems")
        all_problems.extend(problems)
    for problem in all_problems:
        print(f"  {problem}")
    if not all_problems:
        print("All question files are valid.")


if __name__ == "__main__":
    main()
