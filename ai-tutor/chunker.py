"""
Chunker: turns the shipped lesson MDX files into search-ready chunks.

Reads every .mdx under src/content/lessons/, cuts each lesson into sections,
and writes one JSON list to ai-tutor/data/chunks.json.

Cutting rules (decided in the Milestone 1 teach-first session, 2026-09-23):
  - cut at every '## ' heading
  - inside '## Core concepts', also cut at every '### ' heading (one concept per chunk)
  - any section containing <Exercise> blocks is cut once more, one chunk per exercise
  - skip References and Downloads, and skip sections with no text
  - keep short sections but flag them (too_short) so retrieval can treat them differently

Run from the repo root:
    python ai-tutor/chunker.py

Author: Pixels2GenAI Project
"""

import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LESSONS_DIR = REPO_ROOT / "src" / "content" / "lessons"
OUTPUT_FILE = Path(__file__).resolve().parent / "data" / "chunks.json"

# Sections that would pollute search (file names, author names, years).
SKIPPED_SECTIONS = {"references", "downloads"}

# Chunks shorter than this are too thin for search to understand.
MIN_WORDS = 40

# A heading line: 1-6 '#' characters, a space, then the heading text.
HEADING_LINE = re.compile(r"^(#{1,6}) (.+)$")

# An explicit anchor written into a heading, e.g. '## Overview <a id="overview"></a>'.
EXPLICIT_ANCHOR = re.compile(r'<a id="([^"]+)"></a>')


# ---------------------------------------------------------------------------
# Step 1: frontmatter
# ---------------------------------------------------------------------------
def split_frontmatter(file_text):
    """Separate the YAML frontmatter from the lesson body.

    Returns: (frontmatter_text, body_text) as two strings.
    """
    # The file looks like: '---' + frontmatter + '---' + body.
    # Cut at most twice, so a '---' inside the lesson body is never cut again.
    # (20 of 72 lessons have tables whose '|---|' lines would otherwise cut the body
    # short; 2.1.4 would lose about 80% of its text.)
    # That gives three pieces: [0] is empty (nothing before the first '---'),
    # [1] is the frontmatter, [2] is the body.
    pieces = file_text.split("---", 2)
    return pieces[1], pieces[2]


def read_frontmatter_field(frontmatter_text, field_name):
    """Pull one simple value out of the frontmatter, e.g. module: "M 02".

    Returns: the value without quotes, e.g. 'M 02', or None if missing.
    """
    # Pattern for a line like:  title: "Creating Star Fields"
    #   ^ and $       the start and end of ONE line (because of re.MULTILINE)
    #   {field_name}: the field we are looking for, followed by a colon and a space
    #   "(.*)"        the value between the quotes; the brackets capture it
    # All 72 lessons quote 'module' and 'title' with double quotes (checked 2026-09-23).
    pattern = rf'^{field_name}: "(.*)"$'
    match = re.search(pattern, frontmatter_text, re.MULTILINE)

    # re.search returns None when the field is missing; return None instead of crashing.
    if match is None:
        return None
    return match.group(1)


# ---------------------------------------------------------------------------
# Step 3 (used by step 2): heading ids, the same way Astro makes them
# ---------------------------------------------------------------------------
def heading_display_text(raw_heading):
    """The heading text as the browser shows it, which is what Astro slugs.

    '## Concept 2 — `np.clip` in [practice](url) <a id="x"></a>' shows as
    'Concept 2 — np.clip in practice ' (tags, backticks and link targets are not shown).
    """
    text = re.sub(r"<[^>]+>", "", raw_heading)                 # drop HTML/JSX tags like <a id>
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)      # [link text](url) -> link text
    text = text.replace("`", "").replace("**", "").replace("__", "")
    # The site's typography step turns '---' into an em dash and '--' into an en dash
    # before ids are made, so '### Concept 1 -- Grids' gets 'concept-1--grids'
    # (the dash is dropped), not 'concept-1----grids'. Found by the dist/ check on 1.3.2.
    text = text.replace("---", "—").replace("--", "–")
    return text


def slugify(display_text):
    """Copy of github-slugger's rule, which Astro uses for heading ids.

    Lowercase; drop every character that is not a letter, digit, space, hyphen or
    underscore; turn each space into a hyphen. Checked against github-slugger itself:
    'Concept 2 — Uniform vs. Gaussian distributions' -> 'concept-2--uniform-vs-gaussian-distributions'
    (the em dash disappears but both spaces around it stay, hence two hyphens).
    """
    kept_characters = []
    for character in display_text.lower():
        # Unicode categories: L = letters (incl. accented), N = numbers, M = accent marks.
        if unicodedata.category(character)[0] in "LNM" or character in " -_":
            kept_characters.append(character)
    return "".join(kept_characters).replace(" ", "-")


class HeadingIds:
    """Hands out heading ids for one lesson, like Astro's slugger.

    Astro counts EVERY heading (h1-h6) in document order: the second 'Summary'
    becomes 'summary-1'. So every heading line must pass through here, even the
    ones the chunker does not cut at, or later ids would be wrong.
    """

    def __init__(self):
        self.times_seen = {}

    def next_id(self, raw_heading):
        slug = slugify(heading_display_text(raw_heading))
        # github-slugger adds -1, -2 ... to repeats; it counts the slug BEFORE
        # Astro trims a trailing hyphen (e.g. 'Overview ' -> 'overview-' -> 'overview').
        count = self.times_seen.get(slug, 0)
        self.times_seen[slug] = count + 1
        unique_slug = slug if count == 0 else f"{slug}-{count}"
        return unique_slug[:-1] if unique_slug.endswith("-") else unique_slug


def make_anchor(section):
    """The URL anchor that opens this section: /lessons/<id>#<anchor>.

    Decision (option a): use the explicit <a id> when the heading has one (every h2 does),
    otherwise the id Astro generates. Option (b), reading ids from dist/, would need a full
    site build before every chunker run; option (a) only needs the MDX, and
    check_anchors_against_build() below verifies it against dist/ whenever a build exists.
    """
    return section["explicit_anchor"] or section["auto_anchor"]


# ---------------------------------------------------------------------------
# Step 2: sections
# ---------------------------------------------------------------------------
def split_into_sections(body_text):
    """Cut the lesson body into sections at its headings.

    Returns a list of dicts in reading order:
        {"heading": "Concept 2 — Uniform vs. Gaussian distributions",
         "level": 3,
         "explicit_anchor": None,           # or "overview" if the heading has <a id="overview">
         "auto_anchor": "concept-2--uniform-vs-gaussian-distributions",
         "parent_heading": "Core concepts", # the h2 above an h3; None for an h2
         "text": "...all lines until the next cut..."}
    """
    heading_ids = HeadingIds()
    sections = []
    current_section = None      # the section we are adding lines to
    current_h2 = None           # the h2 we are inside, to know whether '###' cuts
    inside_code_fence = False   # lines inside ``` blocks are code, never headings

    for line in body_text.splitlines():
        # A Python comment like '## step 2' inside a code block must not cut the lesson.
        if line.lstrip().startswith("```"):
            inside_code_fence = not inside_code_fence

        heading_match = None if inside_code_fence else HEADING_LINE.match(line)
        if heading_match is None:
            if current_section is not None:
                current_section["text_lines"].append(line)
            continue

        level = len(heading_match.group(1))
        raw_heading = heading_match.group(2)
        auto_anchor = heading_ids.next_id(raw_heading)   # every heading counts, cut or not

        cuts_here = level == 2 or (
            level == 3 and current_h2 is not None and current_h2.lower().startswith("core concepts")
        )
        if not cuts_here:
            # e.g. '### Learning objectives' stays part of its section's text.
            if current_section is not None:
                current_section["text_lines"].append(line)
            continue

        clean_heading = heading_display_text(raw_heading).strip()
        if level == 2:
            current_h2 = clean_heading
        anchor_match = EXPLICIT_ANCHOR.search(raw_heading)
        current_section = {
            "heading": clean_heading,
            "level": level,
            "explicit_anchor": anchor_match.group(1) if anchor_match else None,
            "auto_anchor": auto_anchor,
            "parent_heading": current_h2 if level == 3 else None,
            "text_lines": [],
        }
        sections.append(current_section)

    # Join each section's lines once at the end (cheaper than joining line by line).
    for section in sections:
        section["text"] = "\n".join(section.pop("text_lines"))
    return sections


# ---------------------------------------------------------------------------
# Step 4: exercises
# ---------------------------------------------------------------------------
def split_exercises(section):
    """Cut a section that contains <Exercise> blocks into one piece per exercise.

    Exercises have no heading of their own, so every piece links to the section's
    anchor ('exercises', or e.g. 'synthesis' in the Module 9 template) and gets an
    'id_suffix' ('exercise-1') to keep chunk ids unique.

    Text outside the exercises (the one-line intro, anything after the last one) is
    kept as its own piece only if it is long enough to be useful on its own; the usual
    intro ("Three exercises in Execute → Modify → Create order...") is not.
    """
    pieces = []
    leftover_text = []
    # The lookahead (?=...) cuts BEFORE each <Exercise tag and keeps the tag in the piece.
    for part in re.split(r"(?=<Exercise\b)", section["text"]):
        if not part.startswith("<Exercise"):
            leftover_text.append(part)
            continue
        # Everything after </Exercise> belongs to the section, not to this exercise.
        exercise_text, _, after_exercise = part.partition("</Exercise>")
        leftover_text.append(after_exercise)

        opening_tag = exercise_text.split(">", 1)[0]
        number = re.search(r"n=\{(\d+)\}", opening_tag)
        kicker = re.search(r'kicker="([^"]+)"', opening_tag)
        title = re.search(r'title="([^"]+)"', opening_tag)
        number = number.group(1) if number else str(len(pieces) + 1)
        kicker = kicker.group(1) if kicker else "EXERCISE"
        title = title.group(1) if title else ""

        pieces.append({
            **section,
            "heading": f"Exercise {number} — {kicker}: {title}".rstrip(": "),
            "text": exercise_text,
            "exercise_number": int(number),
            "exercise_kicker": kicker,
            "id_suffix": f"exercise-{number}",
        })

    intro = "\n".join(leftover_text).strip()
    if len(intro.split()) >= MIN_WORDS:
        pieces.insert(0, {**section, "text": intro})
    return pieces


# ---------------------------------------------------------------------------
# Step 5: labels and tidying
# ---------------------------------------------------------------------------
def classify_section(section):
    """Label each chunk so each tutor mode can pick the chunks it needs.

    Hint mode looks at 'exercise' chunks; answer mode mostly at 'concept' ones.
    """
    heading = section["heading"].lower()
    if "exercise_kicker" in section:
        return "exercise"
    if section["level"] == 3 and (section["parent_heading"] or "").lower().startswith("core concepts"):
        return "concept"
    for prefix, section_type in [
        ("overview", "overview"),
        ("quick start", "quick_start"),
        ("core concepts", "concepts_intro"),
        ("exercises", "exercises_intro"),
        ("summary", "summary"),
        ("big question", "big_question"),
        ("part ", "part"),
        ("synthesis", "synthesis"),
    ]:
        if heading.startswith(prefix):
            return section_type
    return "other"


def clean_text(text):
    """Tidy the section text before it is stored.

    Code blocks, figure captions and alt text stay: learners ask about code names
    (np.random.normal), and alt text describes what an output image shows.
    """
    text = EXPLICIT_ANCHOR.sub("", text)        # anchors are metadata, not content
    text = re.sub(r"\n{3,}", "\n\n", text)      # at most one blank line in a row
    return text.strip()


def contains_solution(text):
    """True if the chunk shows a solution dropdown.

    Hint mode must know this: a chunk with the full solution in it makes
    leaking the answer much easier (teach-first part 1).
    """
    return bool(re.search(r'<Dropdown[^>]*summary="[^"]*solution', text, re.IGNORECASE))


# ---------------------------------------------------------------------------
# Wiring the steps together
# ---------------------------------------------------------------------------
def chunk_lesson(mdx_path):
    """Turn one lesson file into a list of chunk dicts."""
    file_text = mdx_path.read_text(encoding="utf-8")
    frontmatter_text, body_text = split_frontmatter(file_text)

    # The numeric prefix of the file name is the lesson id, same rule as
    # generateId in src/content/config.ts (e.g. '2.1.4_stars.mdx' -> '2.1.4').
    lesson_id = mdx_path.stem.split("_")[0]
    module = read_frontmatter_field(frontmatter_text, "module")
    lesson_title = read_frontmatter_field(frontmatter_text, "title")

    sections = []
    for section in split_into_sections(body_text):
        # Exercises live under 'Exercises' in most lessons and under
        # 'Synthesis project' in the Module 9 template, so look for the tag itself.
        if "<Exercise" in section["text"]:
            sections.extend(split_exercises(section))
        else:
            sections.append(section)

    chunks = []
    for section in sections:
        if section["heading"].lower() in SKIPPED_SECTIONS:
            continue
        text = clean_text(section["text"])
        word_count = len(text.split())
        if word_count == 0:
            continue    # e.g. the '## Core concepts' wrapper that only introduces its ###s
        anchor = make_anchor(section)
        chunk_id = f"{lesson_id}#{anchor}"
        if "id_suffix" in section:
            chunk_id += f"/{section['id_suffix']}"
        chunks.append({
            "id": chunk_id,
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "module": module,
            "title": section["heading"],
            "anchor": anchor,
            "url": f"/lessons/{lesson_id}#{anchor}",
            "section_type": classify_section(section),
            "exercise_kicker": section.get("exercise_kicker"),
            "contains_solution": contains_solution(text),
            "text": text,
            "word_count": word_count,
            "too_short": word_count < MIN_WORDS,
        })
    return chunks


def print_stats(chunks):
    """Summary printed after every run, so changes to the rules are visible."""
    word_counts = sorted(chunk["word_count"] for chunk in chunks)
    print(f"chunks:            {len(chunks)} from {len({c['lesson_id'] for c in chunks})} lessons")
    print(f"median words:      {statistics.median(word_counts)}")
    print(f"largest chunk:     {word_counts[-1]} words")
    print(f"under {MIN_WORDS} words:     {sum(chunk['too_short'] for chunk in chunks)}")
    print(f"with a solution:   {sum(chunk['contains_solution'] for chunk in chunks)}")
    print("per section_type:")
    for section_type, count in Counter(chunk["section_type"] for chunk in chunks).most_common():
        print(f"  {section_type:16} {count}")
    duplicate_ids = [chunk_id for chunk_id, count in Counter(c["id"] for c in chunks).items() if count > 1]
    if duplicate_ids:
        print(f"WARNING: {len(duplicate_ids)} duplicate chunk ids, e.g. {duplicate_ids[:3]}")


def check_anchors_against_build(chunks):
    """If the site has been built, confirm every anchor exists in the real HTML.

    Catches the silent failure where a citation link opens the page but not the section.
    Run 'npm run build' first for an up-to-date check; skipped if dist/ is missing.
    """
    built_lessons = REPO_ROOT / "dist" / "lessons"
    if not built_lessons.exists():
        print("anchor check:      skipped (no dist/; run npm run build to enable)")
        return
    missing = []
    for chunk in chunks:
        html_file = built_lessons / f"{chunk['lesson_id']}.html"
        if not html_file.exists():
            missing.append(f"{chunk['id']} (page not built)")
            continue
        if f'id="{chunk["anchor"]}"' not in html_file.read_text(encoding="utf-8"):
            missing.append(chunk["id"])
    unique_anchors = {(c["lesson_id"], c["anchor"]) for c in chunks}
    print(f"anchor check:      {len(unique_anchors) - len(set(missing))} of {len(unique_anchors)} anchors found in dist/")
    for item in missing[:10]:
        print(f"  MISSING {item}")


def main():
    all_chunks = []
    for mdx_path in sorted(LESSONS_DIR.rglob("*.mdx")):
        all_chunks.extend(chunk_lesson(mdx_path))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print_stats(all_chunks)
    check_anchors_against_build(all_chunks)
    print(f"written to {OUTPUT_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
