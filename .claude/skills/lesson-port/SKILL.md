---
name: lesson-port
description: Port a v1 lesson (RST + Python + images) into a v2 MDX lesson with copied assets and wired-up catalog entries. Use when migrating an existing curriculum exercise from numpy-to-genAI into Pixels2GenAI-v2, when the user says "port lesson X.Y.Z", "migrate X.Y.Z to MDX", "bring lesson X.Y.Z into v2", or references a leaf id that doesn't yet have a `lessonSlug` in src/data/subtopics.ts.
---

# Lesson Port Skill — RST → MDX migration

## Skill Overview

This skill handles the canonical workflow for bringing a v1 lesson into v2: it reads the v1 source (RST + Python + outputs), hand-ports the prose into MDX with v2 components, wires up assets through `scripts/copy-v1-assets.mjs`, and updates the curriculum catalog. The lesson is shipped only after passing the `exercise-testing` validation gates.

The bulk of v2's roadmap is porting the remaining 144 v1 lessons. This skill is the operational core of that work.

## When to Use This Skill
- Migrating an existing v1 lesson into v2 for the first time
- Re-porting a lesson after the v1 source has been revised
- Filling in a leaf in `src/data/subtopics.ts` that currently lacks a `lessonSlug`

The reference ports already in v2 — `1.1.1.mdx`, `4.1.1.mdx`, `12.1.2.mdx` — are the canonical examples. Always read at least one before starting a new port.

---

## Step-by-Step Port Workflow

### Step 1: Identify the Lesson

The user gives a leaf id like `4.1.2`. Confirm:

1. The leaf exists in `src/data/subtopics.ts` (it should, since the full catalog is already populated)
2. It does NOT yet have a `lessonSlug` (otherwise it has already been ported)
3. The v1 source folder exists. Path pattern:
   ```
   <v1>\content\Module_NN_<topic>\X.Y_<subtopic>\X.Y.Z_<exercise>\
   ```
   where `<v1>` is `C:\Users\User\Desktop\git-repos\numpy-to-genAI`.

Read the v1 source folder listing to confirm it contains:
- `README.rst` (the canonical prose to hand-port)
- 1-3 Python scripts (Execute / Modify / Create)
- Output `.png` and/or `.gif` files
- Often a `visuals/` subdir with diagram-generation scripts

### Step 2: Determine Framework Type

Use this mapping to select the correct lesson framework. This drives the MDX section layout and the duration/citation budgets.

| Module Range | Framework | Theory/Practice | MDX Structure |
|--------------|-----------|-----------------|---------------|
| Module 0     | F2 (Conceptual)   | 50/50 | Big Question → Parts 1-3 → Synthesis |
| Modules 1-3  | F1 (Hands-On)     | 25/75 | Overview → Quick Start → Core Concepts → Exercises → Summary |
| Module 4     | F1+F2 Hybrid      | 35/65 | Mix of both |
| Modules 5-6  | F1 (Hands-On)     | 25/75 | Overview → Quick Start → Core Concepts → Exercises → Summary |
| Module 7     | F2 (Deep-Dive)    | 50/50 | Big Question → Parts 1-3 → Synthesis |
| Module 8     | F1 (Hands-On)     | 25/75 | Overview → Quick Start → Core Concepts → Exercises → Summary |
| Modules 9-10 | F2 (Deep-Dive)    | 50/50 | Big Question → Parts 1-3 → Synthesis |
| Module 11    | F1 (Hands-On)     | 25/75 | Overview → Quick Start → Core Concepts → Exercises → Summary |
| Modules 12-13| F2 (Deep-Dive)    | 50/50 | Big Question → Parts 1-3 → Synthesis |
| Module 14    | F1 (Hands-On)     | 25/75 | Overview → Quick Start → Core Concepts → Exercises → Summary |
| Module 15    | F3 (Project)      | 20/80 | Phases 1-4 |

The frontmatter `framework` field uses: `"hands-on"`, `"conceptual"`, `"hybrid"`, or `"project"`.

### Step 3: Read Context Files

Before writing any MDX, read in this order:

1. `CLAUDE.md` — project-wide quality standards
2. `src/content/config.ts` — the **lesson frontmatter Zod schema** (authoritative)
3. The closest already-ported sibling lesson under `src/content/lessons/` — for tone and component patterns
4. `thesis_automation/references/scaffolding-rules.md` — Execute/Modify/Create gate criteria
5. `thesis_automation/references/duration-guidelines.md` — duration target for this module range
6. `thesis_automation/references/citation-guidelines.md` — APA + MDX reference list format
7. `thesis_automation/references/visual-guidelines.md` — `<Figure>` usage
8. The v1 `README.rst` and exercise `.py` files for the lesson being ported

### Step 4: Decide What to Carry Over from v1 Source

The v1 `README.rst` is **not** mechanically transformed into MDX. It is the canonical text but should be **hand-edited** during the port. Specifically:

| v1 RST element | v2 MDX treatment |
|----------------|------------------|
| Title + metadata block (`:Duration:`, `:Level:`) | → frontmatter fields |
| RST directive `.. code-block:: python` | → `<CodeBlock lang="python" file="…">` wrapping a fenced code block |
| RST `.. figure::` | → `<Figure src="/lessons/<slug>/…" alt=… caption=… num={N} role="…" />` |
| RST `.. admonition:: tip / note / important` | → `<Admonition type="tip\|note\|important">` |
| RST `.. admonition:: Did You Know?` | → `<Admonition type="dyk" title="Technical note · …">` — and prefer a specific title over generic "Did You Know" (this avoids the X-03 AI pattern) |
| RST `.. dropdown::` | → `<Dropdown summary="…">` |
| RST footnote citations `[Smith2020]_` + `.. [Smith2020] …` | → numeric `[N]` inline + final `<section class="refs"><ol><li>` block |
| RST `:doc:` cross-refs | → markdown link `[label](/lessons/<slug>)` |
| Reflection questions, "What to expect", "Solution" dropdowns | → nest inside `<Exercise>` using `<Dropdown>` |

Heading hierarchy:
- `=====` and `---` underlines → `## h2` (these become the auto-wrapped lesson sections)
- Sub-headings → `### h3` and `#### h4`

Always set `h2` anchor ids: `## Quick start <a id="quick-start"></a>`.

### Step 5: Run the Asset Migrator

Edit `scripts/copy-v1-assets.mjs` and append the new lesson to the `LESSONS` array:

```js
{
  slug: 'X.Y.Z',
  src: 'content/Module_NN_<topic>/X.Y_<subtopic>/X.Y.Z_<exercise>',
  excludes: [],   // add subdirs/files to skip (e.g. '__pycache__', large datasets)
},
```

The migrator's `src` is relative to the **v1 root** (it resolves `../` from the v2 root, which is the user's filesystem assumption — verify this matches the v1 location on the current machine; on this machine v1 lives one folder up at `C:\Users\User\Desktop\git-repos\numpy-to-genAI`).

Then run:
```powershell
npm run copy-assets
```

Confirm the script reports `<N> copied, 0 skipped` for the new slug (where N matches the count of valid asset files in v1). Inspect `public/lessons/<slug>/` to verify everything landed.

The migrator copies: `.png .gif .jpg .jpeg .svg .py .pth .txt`. It **deliberately skips `README.rst`** because the MDX hand-port is the canonical source. It also skips subdirectories — assets from `visuals/` need to be excluded explicitly or moved manually.

### Step 6: Write the MDX File

Create `src/content/lessons/<slug>.mdx`. Skeleton for an F1 (hands-on) lesson:

```mdx
---
module: "M 04"
cycle: "I"
title: "Fractal Square"
objective: "Build self-similar geometry by recursively subdividing a square into nine cells and removing the centre."
framework: "hands-on"
duration: "20–25 min"
level: "beginner-intermediate"
load: "3 core concepts"
prereqs: "Basic Python, NumPy arrays"
prev:
  slug: "1.1.1"
  title: "Images as Arrays & RGB"
next:
  slug: "12.1.2"
  title: "DCGAN Art"
backLink:
  href: "/#curriculum"
  label: "Back to Curriculum"
---

## Overview <a id="overview"></a>

[Opening hook — replace the generic "Fractals are everywhere in nature" with a specific, unusual anchor. See T-X01 in ai-revision.]

### Learning objectives

<ol class="obj-list">
  <li>…</li>
  <li>…</li>
  <li>…</li>
  <li>…</li>
</ol>

## Quick start — [verb phrase] <a id="quick-start"></a>

<CodeBlock lang="python" file="quick_start.py">
```python
# minimal runnable snippet
```
</CodeBlock>

<Figure
  src="/lessons/<slug>/quick_start_output.png"
  alt="…"
  caption="…"
  num={1}
  role="output"
/>

## Core concepts <a id="core-concepts"></a>

### Concept 1 — …

[Prose. Vary sentence length; defer formal definitions; integrate parentheticals.]

### Concept 2 — …

### Concept 3 — …

## Exercises <a id="exercises"></a>

<Exercise n={1} kicker="EXECUTE" title="…">
…
<Dropdown summary="Solution & explanation">…</Dropdown>
</Exercise>

<Exercise n={2} kicker="MODIFY" title="…">
…
</Exercise>

<Exercise n={3} kicker="CREATE" title="…">
<CodeBlock lang="python" file="exercise3_starter.py">
```python
# starter with 3-6 TODOs
```
</CodeBlock>

<Dropdown summary="Hints">…</Dropdown>
<Dropdown summary="Complete solution">…</Dropdown>
</Exercise>

## Downloads <a id="downloads"></a>

<Download href="/lessons/<slug>/main_script.py" label="main_script.py" />

## Summary <a id="summary"></a>

<Admonition title="Key takeaways">
[Single prose paragraph synthesising the 3 concepts. Mix prose with embedded inline lists — avoid bulleted parallelism (X-04).]
</Admonition>

**Common pitfalls to avoid**

- …

## References <a id="references"></a>

<section class="refs">
  <ol>
    <li><span class="tag">[1]</span> Author, A. (YYYY). *Title*. Publisher. <a href="…">link</a></li>
  </ol>
</section>
```

For F2 (conceptual) lessons, replace `## Quick start` + `## Core concepts` with:
```mdx
## Big question <a id="big-question"></a>
## Part 1 — … <a id="part-1"></a>
## Part 2 — … <a id="part-2"></a>
## Part 3 — … <a id="part-3"></a>
## Synthesis project <a id="synthesis"></a>
```

### Step 7: Wire Up the Catalog

Two edits to ship the lesson:

1. **`src/data/subtopics.ts`** — find the leaf entry and add `lessonSlug: '<slug>'`:
   ```ts
   { id: '4.1.2', title: 'Dragon Curve', lessonSlug: '4.1.2' },
   ```

2. **`src/data/modules.ts`** — if this is the *first* ported lesson under a module, set `firstLesson`:
   ```ts
   { idx: '04', title: 'Fractals', em: '& Recursion', fw: 'F1+F2', cycle: 'I', firstLesson: '4.1.2' },
   ```
   If the module already has an earlier ported lesson, leave `firstLesson` alone (it points to the first one in sequence).

Update `prev` / `next` in **both** the new MDX and any sibling MDX whose pointers change. Sibling navigation is hand-maintained in frontmatter, not auto-generated.

### Step 8: Validate

Run the **`exercise-testing`** skill end-to-end. Do not move on until all five levels pass.

### Step 9: Write a Port Log (Optional)

For thesis-trail / supervisor-review purposes, drop a port log at `thesis_automation/reports/<slug>/port_log.md`:

```markdown
# Port Log: X.Y.Z

**Ported**: YYYY-MM-DD
**Framework**: F1 / F2 / F1+F2 / F3
**Status**: SHIPPED / NEEDS REVIEW / BLOCKED

## v1 source
- README.rst: <word count> words
- Scripts: exercise1_*.py, exercise2_*.py, exercise3_*.py
- Output images: <list>

## Asset migration
- LESSONS entry added to scripts/copy-v1-assets.mjs
- npm run copy-assets: <N> copied, <M> skipped
- public/lessons/<slug>/ verified

## Hand-port changes
- [Note any prose changes beyond mechanical RST→MDX translation,
  e.g. "Reworked opening hook (T-X01)", "Removed three trivia boxes,
  integrated content into prose (T-X02)"]

## Validation
- [ ] Level 1: source Python execution
- [ ] Level 2: asset cross-reference
- [ ] Level 3: MDX schema + components
- [ ] Level 4: npm run build + dev render
- [ ] Level 5: quality + AI-pattern audit (LOW or MINIMAL)

## Issues
- None / [list]
```

---

## Quality Gates (Must Pass Before Shipping)

### Duration Targets (from [duration-guidelines.md](../../../thesis_automation/references/duration-guidelines.md))
- **Modules 0-6**: 15-20 minutes maximum
- **Modules 7-15**: 30-45 minutes maximum

### Citation Minimums (from [citation-guidelines.md](../../../thesis_automation/references/citation-guidelines.md))
- Modules 0-6: 5-7 citations
- Modules 7-15: 7-10 citations

### Scaffolding Rules (from [scaffolding-rules.md](../../../thesis_automation/references/scaffolding-rules.md))
- Exercise 1 (Execute): runnable, 3-5 min, reflection questions with Dropdown answers
- Exercise 2 (Modify): 2-5 labeled parameters, numbered Goals, "What to expect" dropdowns
- Exercise 3 (Create): 60-85% complete starter, 3-6 TODOs with what + why explanations, progressive hint Dropdowns, final solution Dropdown

### Cognitive Load
- ≤ 3-4 new concepts across the whole lesson
- ≤ 5 code blocks per `## h2` section
- 4-6 figures maximum

### Code Quality (downloadable `.py` files)
- Simple — clarity over cleverness
- Humanized variable names
- `dtype=np.uint8` for image arrays
- No dependencies outside v1's `requirements.txt`
- Author: "Pixels2GenAI Project" — **NEVER "Claude"**

---

## Post-Port Checklist

- [ ] `src/content/lessons/<slug>.mdx` exists and passes Zod schema
- [ ] Custom components used correctly (`<CodeBlock>`, `<Figure>`, `<Admonition>`, `<Exercise>`, `<Dropdown>`, `<Download>`)
- [ ] `public/lessons/<slug>/` populated by `npm run copy-assets`
- [ ] All `src="/lessons/<slug>/…"` references resolve
- [ ] `src/data/subtopics.ts` has `lessonSlug: '<slug>'` on the right leaf
- [ ] `src/data/modules.ts` `firstLesson` updated if applicable
- [ ] `prev` / `next` frontmatter consistent with sibling lessons
- [ ] `npm run build` succeeds
- [ ] Dev render passes visual + interaction checks
- [ ] AI-revision report shows overall risk LOW or MINIMAL
- [ ] Duration within target range
- [ ] No emojis in MDX prose
- [ ] Source `.py` files credit "Pixels2GenAI Project"

---

**After porting, run the `exercise-testing` skill for end-to-end validation and the `ai-revision` skill for the prose-quality pass. The lesson is shipped only when both gates pass.**
