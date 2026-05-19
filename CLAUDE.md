# CLAUDE.md — Pixels2GenAI v2 Project Guide

This file provides guidance to Claude Code for the **Pixels2GenAI v2** website — the second-generation site for the Pixels2GenAI educational platform.

For deeper guidelines, see the reference documents in [`thesis_automation/references/`](thesis_automation/references/).

---

## Project Overview

**Pixels2GenAI** is an educational platform teaching generative art and AI through 15 progressive modules. The project is a **Master's thesis** using Design-Based Research (DBR) methodology — every module contributes to answering 5 research questions (see "Research Context" below).

**Target audience**: Semi-beginners to semi-experienced programmers interested in creative AI.

**Educational philosophy**: Theory (40%) / Practice (60%). Progressive scaffolding via **Execute → Modify → Create**. Visual-first pedagogy with immediate feedback loops.

### v1 vs v2 — two repositories, one curriculum

The platform has two codebases on this machine:

| Aspect | v1 (`numpy-to-genAI`) | v2 (`Pixels2GenAI-v2`) — this repo |
|--------|------------------------|------------------------------------|
| Tech stack | Sphinx + RST | Astro 5 + React 19 + MDX + TypeScript strict |
| Status | Frozen but live (https://burakkagann.github.io/numpy-to-genAI) | Active rebuild, separate repo, target `pixels2genai.art` |
| Content | All 147 leaf exercises (RST + Python + outputs) | 3 lessons ported (`1.1.1`, `4.1.1`, `12.1.2`); 144 pending |
| Authority | Source of truth for lesson **prose and Python**; treated as **read-only** by v2 | Source of truth for the **published site, design system, MDX components, and curriculum catalog** |
| Location | `C:\Users\User\Desktop\git-repos\numpy-to-genAI` | `C:\Users\User\Desktop\git-repos\Pixels2GenAI-v2` |

The bulk of v2's roadmap is **porting the remaining 144 lessons** from RST into MDX while preserving pedagogical structure and quality standards. Use the **`lesson-port`** skill for that workflow.

---

## Repository Structure

```
Pixels2GenAI-v2/
├── astro.config.mjs                # Astro config + remarkSectionize plugin
├── netlify.toml                    # Netlify build settings
├── package.json                    # npm scripts (dev, build, copy-assets)
├── tsconfig.json
├── public/
│   ├── favicon.svg
│   ├── lessons/<slug>/             # Per-lesson assets (PNG / GIF / .py / .pth)
│   │                               # Populated by scripts/copy-v1-assets.mjs
│   ├── exhibitions/                # Poster + print images for /exhibitions/<id>
│   ├── workshops/                  # Workshop posters + participant gallery
│   ├── research/                   # /research page assets
│   └── explorations/               # Misc visual explorations
├── scripts/
│   └── copy-v1-assets.mjs          # One-shot v1 → public/lessons/ migrator
├── src/
│   ├── layouts/                    # Base.astro, Lesson.astro
│   ├── pages/                      # Astro routes
│   │   ├── index.astro             # Landing page
│   │   ├── 404.astro
│   │   ├── imprint.astro
│   │   ├── research.mdx
│   │   ├── lessons/[slug].astro    # Dynamic lesson route
│   │   ├── exhibitions/<id>.astro  # Per-exhibition pages
│   │   └── workshops/              # index.astro, signup.astro, thanks.astro
│   ├── content/
│   │   ├── config.ts               # Zod schema for lesson frontmatter
│   │   └── lessons/<slug>.mdx      # Lesson content (1.1.1, 4.1.1, 12.1.2)
│   ├── components/
│   │   ├── chrome/                 # Top frame, footer, grain overlay
│   │   ├── cube/                   # React-island JourneyCube + controls
│   │   ├── exhibitions/            # Exhibition specimen + per-show layout
│   │   ├── workshops/              # Workshop specimen + signup form
│   │   ├── lesson/                 # MDX components: Admonition, CodeBlock,
│   │   │                           # Dropdown, Exercise, Figure, Download,
│   │   │                           # plus lesson page chrome
│   │   └── research/               # Research page sections
│   ├── data/                       # Curriculum + event catalogs (source of truth)
│   │   ├── modules.ts              # Flat list of 15 modules + capstone
│   │   ├── subtopics.ts            # Nested subtopics + leaf exercises
│   │   ├── paths.ts                # Painter / Engineer / Architect paths
│   │   ├── research.ts             # 5 RQs + 3 DBR cycles
│   │   ├── exhibitions.ts          # Exhibition catalog
│   │   └── workshops.ts            # Workshop catalog
│   ├── lib/                        # Cube color pipeline (OKLCH→sRGB LUTs)
│   └── styles/                     # Global CSS (tokens, base, typography, prose)
├── thesis_automation/
│   └── references/                 # Quality standards ported from v1
│       ├── scaffolding-rules.md
│       ├── duration-guidelines.md
│       ├── citation-guidelines.md
│       ├── visual-guidelines.md
│       └── ai-revision-framework.md
├── .claude/
│   ├── mcp_servers.json            # MCP servers (filesystem, git, sequential-thinking)
│   └── skills/                     # Project-specific skills
│       ├── ai-revision/            # AI-text pattern detection + transforms
│       ├── exercise-testing/       # 5-level lesson validation pipeline
│       ├── exhibition-ideation/    # Exhibition concept generation
│       └── lesson-port/            # RST → MDX migration workflow
└── CLAUDE.md                       # This file
```

---

## Module Framework Mapping

The curriculum is 15 modules + a capstone, organised across three DBR cycles:

| Module | Topic | Framework | Theory/Practice | Cycle (Stage) |
|--------|-------|-----------|-----------------|----------------|
| 0  | Foundations & Definitions       | F2 (Conceptual)   | 50/50 | I — Foundations |
| 1  | Pixel Fundamentals              | F1 (Hands-On)     | 25/75 | I |
| 2  | Geometry & Mathematics          | F1 (Hands-On)     | 25/75 | I |
| 3  | Transformations & Effects       | F1 (Hands-On)     | 25/75 | I |
| 4  | Fractals & Recursion            | F1+F2 Hybrid      | 35/65 | I |
| 5  | Simulation & Emergent Behaviour | F1 (Hands-On)     | 25/75 | I |
| 6  | Noise & Procedural Generation   | F1 (Hands-On)     | 25/75 | II — Machine Learning |
| 7  | Classical Machine Learning      | F2 (Deep-Dive)    | 50/50 | II |
| 8  | Animation & Time                | F1 (Hands-On)     | 25/75 | II |
| 9  | Neural Networks                 | F2 (Deep-Dive)    | 50/50 | II |
| 10 | TouchDesigner Fundamentals      | F2 (Deep-Dive)    | 50/50 | II |
| 11 | Interactive Systems             | F1 (Hands-On)     | 25/75 | II |
| 12 | Generative AI Models            | F2 (Deep-Dive)    | 50/50 | III — Generative AI |
| 13 | AI + TouchDesigner Integration  | F2 (Deep-Dive)    | 50/50 | III |
| 14 | Data as Material                | F1 (Hands-On)     | 25/75 | III |
| 15 | Capstone Project                | F3 (Project)      | 20/80 | III |

**Framework types**:
- **F1 (Hands-On)**: Overview → Quick Start → Core Concepts → Exercises (Execute/Modify/Create) → Summary
- **F2 (Conceptual)**: Big Question → Part 1-3 → Synthesis Project
- **F3 (Project)**: Overview → Phase 1-4 → Community Showcase

The canonical curriculum data is in [`src/data/modules.ts`](src/data/modules.ts) (flat catalog) and [`src/data/subtopics.ts`](src/data/subtopics.ts) (nested with ~147 leaf exercises). Each leaf has an optional `lessonSlug` pointing to a `src/content/lessons/<slug>.mdx`.

---

## Shipping a Lesson (the two-step workflow)

A v2 lesson is "shipped" — i.e. appears as a clickable card on the landing page — when **both** of these are in place:

1. **MDX file** at `src/content/lessons/<slug>.mdx`, schema-valid against [`src/content/config.ts`](src/content/config.ts), with assets under `public/lessons/<slug>/`.
2. **`lessonSlug: '<slug>'`** added to the matching leaf in [`src/data/subtopics.ts`](src/data/subtopics.ts). If this is the module's first ported lesson, also update `firstLesson` in [`src/data/modules.ts`](src/data/modules.ts).

Until step 2 happens, the leaf renders as "Coming soon" (dim) and is unreachable. Use the **`lesson-port`** skill for the full workflow including v1→MDX hand-port, asset migration, and catalog wiring; then **`exercise-testing`** to validate, then **`ai-revision`** for the prose-quality pass.

### MDX lesson schema (lesson frontmatter)

```yaml
---
module: "M 04"             # Display label
cycle: "I"                 # I | II | III
title: "…"
objective: "One-sentence italic lead under the H1."
framework: "hands-on"      # hands-on | conceptual | hybrid | project
duration: "20–25 min"
level: "beginner"          # beginner | beginner-intermediate | intermediate | intermediate-advanced | advanced
load: "3 core concepts"    # optional cognitive-load chip
prereqs: "Basic Python"    # optional
prev: { slug: "1.1.1", title: "…" }   # or null
next: { slug: "12.1.2", title: "…" }  # or null
backLink: { href: "/#curriculum", label: "Back to Curriculum" }
---
```

### Custom MDX components

| Component | Purpose |
|-----------|---------|
| `<CodeBlock lang="python" file="…">` | Wraps fenced code blocks; dual-theme Shiki highlights |
| `<Admonition type="tip\|note\|important\|dyk" title="…">` | Pull-out boxes; prefer specific titles over generic "Did You Know" |
| `<Figure src=… alt=… caption=… num={N} role="diagram\|output">` | All images |
| `<Exercise n={1} kicker="EXECUTE\|MODIFY\|CREATE" title="…">` | Exercise wrappers |
| `<Dropdown summary="…">` | Collapsible hints / solutions / answers |
| `<Download href=… label=…>` | Asset download links |

The remark plugin in `astro.config.mjs` auto-wraps content between `## h2` headings into `<section class="lesson-section">` (drives the manuscript-margin side-rail).

---

## Quality Standards (Non-Negotiable)

### Code Quality
- All scripts must execute without errors on Python 3.11.9 (v1's venv), Windows 11
- Scripts must be simple — prioritise clarity over cleverness
- Well-annotated code with inline comments explaining **why**, not what
- Humanized variable names (`pixel_color` not `pc`)
- No dependencies outside v1's `requirements.txt` without approval
- **NEVER use "Claude" as author** — use **"Pixels2GenAI Project"**

### Documentation Quality
- Academic yet friendly tone (like a patient teacher)
- **No emojis** in lesson MDX or downloadable scripts
- All factual claims cited (APA 7th edition; see [`thesis_automation/references/citation-guidelines.md`](thesis_automation/references/citation-guidelines.md))
- Use the v2 custom MDX components, not raw HTML, for admonitions / figures / exercises / dropdowns
- Every Core Concept should have at least one `<Figure>`

### Exercise Scaffolding (Execute → Modify → Create)
- **Exercise 1 (Execute)**: complete runnable script, 3-5 min, reflection questions with `<Dropdown>` answers
- **Exercise 2 (Modify)**: 2-5 labeled parameters (CONFIG section or inline edit zones), 8-12 min, numbered Goals each with "What to expect" dropdown
- **Exercise 3 (Create)**: 60-85% complete starter, 3-6 TODOs with what + why, 10-15 min, progressive hint Dropdowns + final solution Dropdown, "Make It Your Own" section
- Full details: [`thesis_automation/references/scaffolding-rules.md`](thesis_automation/references/scaffolding-rules.md)

### Duration Targets
- **Modules 0-6**: 15-20 minutes maximum (target: 18 min avg)
- **Modules 7-15**: 30-45 minutes maximum (target: 40 min avg)
- **Cognitive load**: ≤ 3-4 new concepts per lesson, ≤ 5 code blocks per `## h2` section
- Full details: [`thesis_automation/references/duration-guidelines.md`](thesis_automation/references/duration-guidelines.md)

### Citations
- **Modules 0-6**: 5-7 citations minimum (APA 7th edition)
- **Modules 7-15**: 7-10 citations minimum
- Rendered in MDX as a numbered list inside `<section class="refs"><ol><li>...</li></ol></section>`
- Full details: [`thesis_automation/references/citation-guidelines.md`](thesis_automation/references/citation-guidelines.md)

### Visuals
- Every image must serve a pedagogical purpose
- Output images: < 500 KB, PNG for static, GIF for animations
- Animated diagrams: 700×380px, 15 FPS, < 500 KB
- Include `alt=` and `caption=` on every `<Figure>`
- Full details: [`thesis_automation/references/visual-guidelines.md`](thesis_automation/references/visual-guidelines.md)

---

## Asset Migration (v1 → public/lessons/)

[`scripts/copy-v1-assets.mjs`](scripts/copy-v1-assets.mjs) copies PNG / GIF / JPG / SVG / PY / PTH / TXT from v1 lesson folders into `public/lessons/<slug>/`. It:

- Treats v1 as **read-only**
- Is **idempotent** — re-running overwrites destination files
- Deliberately **skips `README.rst`** (the MDX hand-port is canonical)
- Skips subdirectories — exclude or move manually if needed

To add a new lesson to the migrator, append an entry to its `LESSONS` array:

```js
{ slug: '4.1.2', src: 'content/Module_04_fractals_recursion/4.1_classical_fractals/4.1.2_dragon_curve', excludes: [] }
```

Then run `npm run copy-assets`.

---

## Hardware & Environment

- **OS**: Windows 11
- **Shell**: PowerShell (primary), Bash also available
- **Node**: 20 (LTS) — version pinned in `.nvmrc`
- **Python**: 3.11.9 (v1's venv at `<v1>\.venv\Scripts\`)
- **GPU**: Nvidia RTX 5070Ti (CUDA-enabled) — used for v1-source scripts in Modules 9, 12, 13
- **TouchDesigner**: Licensed (Modules 10, 11, 13)

For GPU-intensive lessons (9, 12, 13), v1 scripts use:
```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
```

---

## Quick Start Commands

```powershell
# Install dependencies (one-time)
npm install

# Copy lesson assets from v1 (run after adding to LESSONS array)
npm run copy-assets

# Dev server (http://localhost:4321)
npm run dev

# Production build (output to dist/)
npm run build

# Preview the production build
npm run preview
```

---

## Research Context (Thesis)

This project follows **Design-Based Research (DBR)** methodology with 5 research questions. The full RQ list is in [`src/data/research.ts`](src/data/research.ts):

- **RQ1 — Framework Design**: pedagogical principles scaffolding arrays → generative AI
- **RQ2 — Cognitive Load**: decomposing complex concepts under cognitive-load constraints
- **RQ3 — Integration Pathways**: real-time systems (TouchDesigner) ⨯ progressive AI learning
- **RQ4 — Assessment**: technical proficiency, creative expression, conceptual understanding
- **RQ5 — Transfer**: how learners transfer foundational concepts to novel creative AI contexts

### DBR Cycles
- **Cycle I — Foundations**: Modules 00-05
- **Cycle II — Machine Learning**: Modules 06-11
- **Cycle III — Generative AI**: Modules 12-15

Cycle data is in `src/data/research.ts` (`CYCLES`). The exhibition (March 2026, Berlin) and workshop (Feb 2026, Berlin) data — already populated as past events — is in `src/data/exhibitions.ts` and `src/data/workshops.ts`.

---

## Essential Rules

1. **NEVER auto-commit** — user always commits manually
2. **NEVER use "Claude" as author** — use **"Pixels2GenAI Project"**
3. **No emojis** in MDX prose or downloadable `.py` files
4. **All claims must be cited** — APA 7th edition
5. **Quality over speed** — each lesson is a polished educational resource
6. **Test everything** — `npm run build` must succeed; dev render must look right before shipping
7. **Follow scaffolding** — Execute → Modify → Create for every exercise set
8. **Stay within duration** — 15-20 min (Modules 0-6), 30-45 min (Modules 7-15)
9. **v1 is read-only** — never modify files under `numpy-to-genAI/`; if v1 source has a bug, document it in the port log and work around it in v2
10. **Ship a lesson in two steps** — drop the MDX, then add the `lessonSlug` to `src/data/subtopics.ts`

---

## Skills

Project-specific skills live in [`.claude/skills/`](.claude/skills/):

| Skill | Use when |
|-------|----------|
| [`lesson-port`](.claude/skills/lesson-port/SKILL.md) | Porting a v1 lesson (RST + Python + images) into a v2 MDX lesson |
| [`exercise-testing`](.claude/skills/exercise-testing/SKILL.md) | Validating a v2 lesson before shipping (5-level gate) |
| [`ai-revision`](.claude/skills/ai-revision/SKILL.md) | Detecting AI patterns in lesson prose and applying targeted transforms |
| [`exhibition-ideation`](.claude/skills/exhibition-ideation/SKILL.md) | Generating new exhibition-print concepts that combine module techniques |

Typical workflow for shipping a ported lesson:
```
lesson-port  →  exercise-testing  →  ai-revision  →  ship (update subtopics.ts)
```

---

## Reference Documents

For detailed guidelines, read these files in [`thesis_automation/references/`](thesis_automation/references/):

| Document | Contents |
|----------|----------|
| [`scaffolding-rules.md`](thesis_automation/references/scaffolding-rules.md) | Execute / Modify / Create pass criteria, red flags, CONFIG vs inline edit zones |
| [`duration-guidelines.md`](thesis_automation/references/duration-guidelines.md) | Duration estimation formulas, cognitive load limits, trimming guidelines |
| [`citation-guidelines.md`](thesis_automation/references/citation-guidelines.md) | APA 7th edition formats, MDX rendering, quality checklist |
| [`visual-guidelines.md`](thesis_automation/references/visual-guidelines.md) | When to create visuals, technical requirements, `<Figure>` embedding |
| [`ai-revision-framework.md`](thesis_automation/references/ai-revision-framework.md) | AI pattern detection taxonomy, risk levels, transformation techniques |

---

## Troubleshooting

**MDX schema error on `npm run build`** — open `src/content/config.ts` and check the failing field against the Zod schema. Common: `framework` value not in the enum, missing required `title` or `objective`.

**`<Figure src="/lessons/<slug>/foo.png">` shows broken image** — the asset is missing from `public/lessons/<slug>/`. Re-run `npm run copy-assets` or copy the file in manually.

**Dev server doesn't pick up a new lesson** — Astro caches `src/content/lessons/`. Restart `npm run dev`.

**`tsc` complains about an MDX import** — make sure the lesson is referenced through Content Collections (`getCollection('lessons')`), not directly. See `src/pages/lessons/[slug].astro`.

**v1 Python script fails in v1 venv** — v1 is read-only. Document the failure in the port log; port the existing output PNG and either skip the broken example or write a v2-side replacement script under `public/lessons/<slug>/`.

**Lesson card still says "Coming soon" after dropping the MDX** — you missed step 2 of the ship workflow. Add `lessonSlug: '<slug>'` to the matching leaf in `src/data/subtopics.ts`.

---

*Adapted from v1 CLAUDE.md (numpy-to-genAI) with stack and workflow rewritten for v2. The pedagogy, quality standards, and research framing are unchanged — only the surface (Astro/MDX vs Sphinx/RST) is different.*
