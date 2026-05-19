---
name: exercise-testing
description: Comprehensive validation for Pixels2GenAI v2 lessons. Use when validating ported v1 Python scripts, checking copied lesson assets, type-checking MDX frontmatter, running the Astro build, or performing quality audits on a lesson. Activate after porting a lesson, before marking a lesson as shipped, or when debugging build/render errors.
---

# Lesson Testing & Validation Skill (v2)

## Skill Overview
This skill provides comprehensive validation protocols for v2 lessons. A "lesson" in v2 is the combination of an MDX file under `src/content/lessons/`, the assets it references under `public/lessons/<slug>/`, and the leaf entry in `src/data/subtopics.ts`. Validation makes sure every layer is consistent before the lesson goes live.

## When to Use This Skill
- After porting a v1 lesson (RST → MDX) — use alongside the `lesson-port` skill
- After authoring a new MDX lesson from scratch
- Before marking a lesson as shipped (i.e. before adding `lessonSlug` in `subtopics.ts`)
- When debugging build / render errors
- During quality assurance reviews

## Testing Hierarchy

```
Level 1: Source Python Execution      (MUST PASS for ported lessons)
    ↓
Level 2: Asset Migration & Validation (MUST PASS)
    ↓
Level 3: MDX Frontmatter + Content    (MUST PASS)
    ↓
Level 4: Astro Build + Render         (MUST PASS)
    ↓
Level 5: Quality Audit                (CHECKLIST)
```

---

## Level 1: Source Python Execution

**Goal**: Verify the v1-source Python scripts still execute, since their outputs are the static images embedded in the v2 lesson.

This applies only when **porting** a lesson from v1. For lessons authored natively in v2, skip to Level 2.

### Manual Testing
```powershell
# Navigate to the v1 exercise directory
$v1 = "C:\Users\User\Desktop\git-repos\numpy-to-genAI"
Set-Location "$v1\content\Module_XX_topic\X.Y_subtopic\X.Y.Z_exercise"

# Activate the v1 venv (Python 3.11.9)
& "$v1\.venv\Scripts\Activate.ps1"

# Run each script
python exercise1_execute.py
python exercise2_modify.py
python exercise3_create.py
# Exit code 0 = pass
```

### Common Source Errors

**`ModuleNotFoundError`** — venv missing a dependency. Compare against `<v1>\requirements.txt`.

**`FileNotFoundError`** — script depends on a relative path. Confirm the working directory matches the exercise folder.

**Array dimension mismatch** — usually a NumPy version skew between v1's venv and a fresh Python.

If a v1 script fails, **do not silently fix it in v1** (v1 is treated as read-only). Instead: document the failure, port the *current* working output PNG/GIF, and either skip the broken example in the MDX or write a v2-equivalent script under `public/lessons/<slug>/`.

---

## Level 2: Asset Migration & Validation

**Goal**: Verify that every image, GIF, and downloadable `.py` referenced from the MDX exists under `public/lessons/<slug>/`.

### Step 2.1 — Run the migrator

For each lesson being ported, add its v1 source path to the `LESSONS` array in `scripts/copy-v1-assets.mjs`, then:

```powershell
npm run copy-assets
```

The script copies PNG/GIF/JPG/SVG/PY/PTH/TXT into `public/lessons/<slug>/` and is **idempotent** — re-running overwrites destination files. It deliberately **skips `README.rst`** because the MDX hand-port is canonical.

### Step 2.2 — Cross-reference MDX assets

For every `src="/lessons/<slug>/…"` in the MDX, verify the file exists:

```powershell
# Inside the lesson dir, list everything that was copied
Get-ChildItem -Recurse "public/lessons/<slug>/"
```

Then grep the MDX for every `/lessons/<slug>/` reference and confirm each filename appears in the directory listing.

### Step 2.3 — Image sanity checks

For each PNG / GIF / JPG in `public/lessons/<slug>/`:

- Opens cleanly (no zero-byte / truncated files)
- File size <= 500 KB for PNGs, <= 2 MB for GIFs (see `thesis_automation/references/visual-guidelines.md`)
- Dimensions between 10×10 and 4096×4096

Quick PowerShell check:
```powershell
Get-ChildItem "public/lessons/<slug>/*.png" | ForEach-Object {
  $kb = [math]::Round($_.Length / 1KB, 1)
  "$($_.Name): $kb KB"
}
```

### Checklist
- [ ] All `<Figure src=…>` paths resolve under `public/lessons/<slug>/`
- [ ] All `<Download href=…>` paths resolve under `public/lessons/<slug>/`
- [ ] Image file sizes within budget
- [ ] No leftover `__pycache__`, `.pyc`, `.ipynb_checkpoints` in `public/lessons/<slug>/`
- [ ] Model-weight files (`.pth`) intentionally excluded if large (e.g. fabric dataset in 12.1.2)

---

## Level 3: MDX Frontmatter + Content

**Goal**: Verify the MDX file is valid against the Zod schema in `src/content/config.ts` and uses the custom MDX components correctly.

### Step 3.1 — Frontmatter schema check

The schema (in [src/content/config.ts](../../../src/content/config.ts)) requires:

```yaml
---
module: "M 04"             # display label
cycle: "I"                  # I | II | III
title: "Fractal Square"
objective: "One-sentence italic lead."
framework: "hands-on"       # hands-on | conceptual | hybrid | project
duration: "20–25 min"
level: "beginner"           # beginner | beginner-intermediate | intermediate | intermediate-advanced | advanced
load: "3 core concepts"     # optional
prereqs: "Basic Python"     # optional
prev: { slug: "1.1.1", title: "Images as Arrays & RGB" }  # or null
next: { slug: "12.1.2", title: "DCGAN Art" }              # or null
backLink: { href: "/#curriculum", label: "Back to Curriculum" }  # optional
---
```

The build fails fast if any required field is missing or has the wrong shape — `npm run build` is the authoritative check (Astro runs Zod under the hood).

### Step 3.2 — Custom component sanity

Required components (defined in `src/components/lesson/`):

| Component | Usage |
|-----------|-------|
| `<CodeBlock lang="python" file="…">` | Wraps fenced code blocks |
| `<Admonition type="tip\|note\|important\|dyk" title="…">` | Pull-out boxes; `dyk` = "Did You Know" but PREFER a specific title |
| `<Figure src=… alt=… caption=… num={N} role="diagram\|output">` | All images |
| `<Exercise n={1} kicker="EXECUTE" title="…">` | Exercise wrappers (kickers: EXECUTE, MODIFY, CREATE) |
| `<Dropdown summary="…">` | Collapsible hint/solution blocks |
| `<Download href=… label=…>` | Asset download links |

### Step 3.3 — Sectionize check

The Astro config (`astro.config.mjs`) auto-wraps content between `## h2` headings into `<section class="lesson-section">`. Confirm:

- Lesson has clear `## h2` headings (typically: Overview, Quick start, Core concepts, Exercises, Downloads, Summary, References)
- Content before the first `h2` (e.g. an opening `<Figure>`) is intentional — it stays unwrapped at article level

### Content Completeness Checklist (matches [scaffolding-rules.md](../../../thesis_automation/references/scaffolding-rules.md))

**Hands-on (F1) lessons must have**:
- [ ] Overview (anchor `#overview`)
- [ ] Learning objectives (`<ol class="obj-list">`)
- [ ] Quick start (`#quick-start`) with a runnable snippet and visible output
- [ ] Core concepts (`#core-concepts`) — 2-3 concepts
- [ ] Exercises (`#exercises`) — Execute / Modify / Create using `<Exercise>` wrappers
- [ ] Downloads (`#downloads`)
- [ ] Summary (`#summary`)
- [ ] References (`#references`) — `<section class="refs">` with `<ol>`

**Conceptual (F2) lessons must have**:
- [ ] Big Question (or hook paragraph)
- [ ] Learning path overview
- [ ] Part 1-3 sections with theory + code
- [ ] Exercises (Execute / Modify / Create)
- [ ] Synthesis project
- [ ] Summary + References (7-10 citations)

---

## Level 4: Astro Build + Render

**Goal**: Verify the lesson builds, renders, and is reachable.

### Step 4.1 — Full build

```powershell
npm run build
```

Look for:
- Zero MDX compilation errors
- Zero broken `<Figure src=…>` paths (Astro will warn if a `/lessons/<slug>/…` file is missing from `public/`)
- TypeScript strict passes (`@astrojs/check` runs as part of build)
- Output written to `dist/lessons/<slug>/index.html`

### Step 4.2 — Dev server render

```powershell
npm run dev
```

Open `http://localhost:4321/lessons/<slug>` and verify:
- Page loads with no console errors
- All figures display (right-click → "open in new tab" any that look broken)
- All `<Dropdown>` blocks expand
- All `<CodeBlock>` blocks render with the dual-theme Shiki highlighting
- The lesson-section side-rail (manuscript-margin gloss) tracks each `<h2>` section
- The stage tracker shows the right module window (driven by `module:` frontmatter)
- `prev` / `next` navigation links resolve to existing lessons

### Step 4.3 — Lighthouse / accessibility quick check (optional)

In Chrome DevTools, run Lighthouse on the rendered page. Watch for missing alt text on images — every `<Figure>` should have a meaningful `alt`.

---

## Level 5: Quality Audit

**Goal**: Comprehensive review of content quality.

### Pedagogical Quality Checklist (from CLAUDE.md)

- [ ] **Tone**: Academic yet friendly (no emojis)
- [ ] **Author attribution**: Source `.py` files credit "Pixels2GenAI Project", never "Claude"
- [ ] **Citations**: Min 5-7 (Modules 0-6) or 7-10 (Modules 7-15); APA 7th edition; rendered in `<section class="refs">`
- [ ] **Accuracy**: Technical information correct (cross-check against module references)
- [ ] **Clarity**: Concepts explained without jargon overload
- [ ] **Completeness**: Follows appropriate framework template (F1 / F2 / F1+F2 / F3)
- [ ] **Scaffolding**: Exercises progress Execute → Modify → Create
- [ ] **Visual examples**: Every Core Concept has at least one figure
- [ ] **Accessibility**: Descriptive alt text on every `<Figure>`
- [ ] **Duration**: Within target range for the module (see [duration-guidelines.md](../../../thesis_automation/references/duration-guidelines.md))
- [ ] **Cognitive load**: ≤ 3-4 new concepts across the lesson

### Code Quality Checklist (for downloadable `.py` files)

- [ ] Simplicity — no unnecessary complexity
- [ ] Comments explain "why", not "what"
- [ ] Humanized variable names (`pixel_color` not `pc`)
- [ ] `dtype=np.uint8` for image arrays
- [ ] Only dependencies from v1's `requirements.txt`
- [ ] Reasonable execution time (< 30 s for most lessons)
- [ ] Reproducible (random seeds set where relevant)

### AI-pattern check

Before final approval, run the **ai-revision** skill against the MDX file. Aim for overall risk LOW or MINIMAL.

---

## Success Criteria

A lesson is ready to ship (i.e. ready to receive its `lessonSlug` in `src/data/subtopics.ts`) when:

1. ✅ Source Python scripts execute cleanly (Level 1 — for ported lessons)
2. ✅ Assets are copied and every MDX reference resolves (Level 2)
3. ✅ MDX is schema-valid and uses components correctly (Level 3)
4. ✅ `npm run build` succeeds with no errors or asset warnings (Level 4)
5. ✅ Dev-server render passes visual + interaction checks (Level 4)
6. ✅ Content meets pedagogical and AI-pattern quality bars (Level 5)

Only then should you update `src/data/subtopics.ts` to add `lessonSlug` for the leaf, and `src/data/modules.ts` to update `firstLesson` if this is the module's first ported lesson.

---

**Use the `lesson-port` skill for the porting workflow itself and `ai-revision` for the prose quality pass. This skill is the gate that ensures everything fits together before going live.**
