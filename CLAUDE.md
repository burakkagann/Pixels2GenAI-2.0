# CLAUDE.md — Pixels2GenAI v2 Project Guide

This file provides guidance to Claude Code for the **Pixels2GenAI v2** website — the second-generation site for the Pixels2GenAI educational platform.

For deeper guidelines, see the reference documents in [`docs/references/`](docs/references/). Curriculum structure and research framing live in [`docs/curriculum.md`](docs/curriculum.md).

---

## Project Overview

**Pixels2GenAI** is an educational platform teaching generative art and AI through 15 progressive modules + a capstone (193 leaf exercises). The project is a **Master's thesis** using Design-Based Research (DBR) methodology — every module contributes to answering 5 research questions (see [`docs/curriculum.md`](docs/curriculum.md)).

**Target audience**: Semi-beginners to semi-experienced programmers interested in creative AI.

**Educational philosophy**: Theory (40%) / Practice (60%). Progressive scaffolding via **Execute → Modify → Create**. Visual-first pedagogy with immediate feedback loops.

### v1 vs v2 — two repositories, one curriculum

The platform has two codebases on this machine:

| Aspect | v1 (`numpy-to-genAI`) | v2 (`Pixels2GenAI-v2`) — this repo |
|--------|------------------------|------------------------------------|
| Tech stack | Sphinx + RST | Astro 5 + React 19 + MDX + TypeScript strict |
| Status | Frozen but live (https://burakkagann.github.io/numpy-to-genAI) | Live at `pixels2genai.art`; lessons ported module by module (`npm run status` for the current count) |
| Content | All leaf exercises (RST + Python + outputs) | MDX hand-ports of the same curriculum |
| Authority | Source of truth for lesson **prose and Python**; treated as **read-only** by v2 | Source of truth for the **published site, design system, MDX components, and curriculum catalog** |
| Location | `C:\Users\User\Desktop\git-repos\numpy-to-genAI` | `C:\Users\User\Desktop\git-repos\Pixels2GenAI-v2` |

v2's content tree mirrors v1's `content/` hierarchy verbatim (same `Module_xx_…/x.y_…/x.y.z_…` folder names), so navigating between the repos during a port is 1:1. Use the **`lesson-port`** skill for that workflow.

---

## Repository Structure

```
Pixels2GenAI-v2/
├── astro.config.mjs                # Astro config + remarkSectionize plugin
├── netlify.toml                    # Netlify build, redirects, cache headers
├── package.json                    # npm scripts (dev, build, check, status, copy-assets)
├── tsconfig.json
├── docs/
│   ├── curriculum.md               # Module framework mapping + research context
│   ├── references/                 # Quality standards ported from v1
│   │   ├── scaffolding-rules.md
│   │   ├── duration-guidelines.md
│   │   ├── citation-guidelines.md
│   │   ├── visual-guidelines.md
│   │   └── ai-revision-framework.md
│   └── reports/                    # Generated artifacts (migration-inventory.json)
├── public/
│   ├── favicon.svg
│   ├── lesson-media/               # Per-lesson assets (PNG / GIF / .py / .pth),
│   │   └── Module_xx_…/x.y_…/x.y.z_…/   #   mirrors src/content/lessons/ exactly
│   ├── exhibitions/                # Poster + print images for /exhibitions/<id>
│   ├── workshops/                  # Workshop posters + participant gallery
│   ├── research/                   # /research page assets
│   └── explorations/               # Misc visual explorations
├── scripts/
│   ├── check-lessons.mjs           # Lesson integrity check (npm run check, gates build)
│   ├── lesson-status.mjs           # Per-module progress table (npm run status)
│   ├── copy-v1-assets.mjs          # v1 → public/lesson-media/ asset migrator
│   ├── gen-icons.mjs               # Favicon / touch-icon generator
│   ├── lib/catalog.mjs             # Shared catalog + path resolver for all tooling
│   └── migration/                  # Archived one-shots (inventory, stubs, figure gens,
│                                   #   restructure manifest) — not part of daily workflow
├── src/
│   ├── layouts/                    # Base.astro, Lesson.astro, Research
│   ├── pages/                      # Astro routes
│   │   ├── index.astro             # Landing page
│   │   ├── 404.astro / imprint / privacy / research.mdx
│   │   ├── lessons/[slug].astro    # Dynamic lesson route (slug = numeric leaf id)
│   │   ├── og/[...route].ts        # Build-time OG card images
│   │   ├── exhibitions/<id>.astro  # Per-exhibition pages
│   │   ├── announce/               # Announcements signup + thanks
│   │   └── workshops/              # index.astro
│   ├── content/
│   │   ├── config.ts               # Glob loader (generateId → numeric id) + Zod schema
│   │   └── lessons/                # Lesson MDX, mirrors v1's content/ tree:
│   │       └── Module_xx_…/x.y_…/x.y.z_<name>.mdx
│   ├── components/
│   │   ├── chrome/                 # Top frame, footer, grain overlay
│   │   ├── cube/                   # React-island JourneyCube + controls
│   │   ├── exhibitions/            # Exhibition specimen + per-show layout
│   │   ├── workshops/              # Workshop specimen + signup form
│   │   ├── lesson/                 # Lesson chrome + mdx/ component kit
│   │   └── research/               # Research page sections
│   ├── data/
│   │   ├── curriculum/             # modules.ts (flat catalog), subtopics.ts (leaves)
│   │   └── site/                   # research.ts, exhibitions.ts, workshops.ts
│   ├── lib/                        # Cube color pipeline (OKLCH→sRGB LUTs)
│   └── styles/                     # Global CSS (tokens, base, typography, prose)
├── .claude/
│   └── skills/                     # lesson-port, exercise-testing, ai-revision,
│                                   #   exhibition-ideation
└── CLAUDE.md                       # This file
```

---

## Lesson Layout & URLs

A lesson has three coordinates, all keyed by its **numeric leaf id** (e.g. `2.1.1`):

- **MDX**: `src/content/lessons/Module_02_geometry_mathematics/2.1_basic_shapes_primitives/2.1.1_lines.mdx`
- **Assets**: `public/lesson-media/Module_02_geometry_mathematics/2.1_basic_shapes_primitives/2.1.1_lines/` (same path, leaf is a folder)
- **URL**: `/lessons/2.1.1` — **stable forever**; the glob loader's `generateId` in [`src/content/config.ts`](src/content/config.ts) extracts the numeric prefix of the filename, so the URL never depends on where the file lives or what it's called after the prefix

Folder and file names are copied **verbatim from v1's `content/` tree**. Asset URLs inside MDX look like `/lesson-media/Module_02_…/2.1_…/2.1.1_lines/simple_line.png`; cross-lesson links stay `/lessons/<id>`. `scripts/lib/catalog.mjs` (`lessonAssetLocation`) is the single path resolver — never hand-derive these paths in tooling.

The canonical curriculum data is in [`src/data/curriculum/modules.ts`](src/data/curriculum/modules.ts) (flat catalog) and [`src/data/curriculum/subtopics.ts`](src/data/curriculum/subtopics.ts) (nested, 193 leaves). Each leaf has an optional `lessonSlug` — the numeric id of its lesson.

---

## Shipping a Lesson (the two-step workflow)

A v2 lesson is "shipped" — i.e. appears as a clickable card on the landing page — when **both** of these are in place:

1. **MDX file** under `src/content/lessons/<Module dir>/<subtopic dir>/<id>_<name>.mdx` (v1-mirrored path), schema-valid against [`src/content/config.ts`](src/content/config.ts), with assets under the matching `public/lesson-media/…/<id>_<name>/`.
2. **`lessonSlug: '<id>'`** added to the matching leaf in [`src/data/curriculum/subtopics.ts`](src/data/curriculum/subtopics.ts). If this is the module's first ported lesson, also update `firstLesson` in [`src/data/curriculum/modules.ts`](src/data/curriculum/modules.ts).

Until step 2 happens, the leaf renders as "Coming soon" (dim) and is unreachable. Use the **`lesson-port`** skill for the full workflow including v1→MDX hand-port, asset migration, and catalog wiring; then **`exercise-testing`** to validate, then **`ai-revision`** for the prose-quality pass. `npm run check` validates all of this wiring and gates the build.

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

## SEO & Structured Data

The site emits JSON-LD structured data and an RSS feed for search + AI-answer-engine (AEO/GEO) visibility. Most updates automatically; **two items need manual upkeep — don't forget them.**

**Automatic — no action when shipping lessons:**
- **RSS feed** — [`src/pages/feed.xml.ts`](src/pages/feed.xml.ts) lists every lesson via `getCollection('lessons')`; new lessons appear on the next build. Discovery `<link>` is in `Base.astro`.
- **Breadcrumb JSON-LD** — `BreadcrumbList` built in [`src/layouts/Lesson.astro`](src/layouts/Lesson.astro) from the slug + `MODULES`/`SUBTOPICS`. Populates automatically once `lessonSlug` is wired into `subtopics.ts` (already step 2 of the ship workflow). Degrades gracefully if a module/subtopic isn't catalogued.
- **LearningResource** (per lesson) + **Course** (homepage) JSON-LD — frontmatter/data driven.
- `Base.astro`'s `jsonLd` prop accepts a single object **or an array** (multiple blocks per page).

**Manual upkeep — easy to forget:**
- **Research page `Article` schema** — `dateModified` lives in [`src/pages/research.mdx`](src/pages/research.mdx) frontmatter, **not** the build clock. **Bump it whenever you substantively edit the research page** (this is correct AEO behavior — only bump on real edits). Also keep `author` / `datePublished` accurate.
- **Lesson FAQ schema** — opt-in per lesson via an optional `faq: [{ q, a }]` frontmatter array (schema in [`src/content/config.ts`](src/content/config.ts)), emitted as `FAQPage` JSON-LD by `Lesson.astro`. **New lessons get NO FAQ markup unless you add the field.** Only add Q&A that is **also visible on the page** (mirror the reflection-question dropdowns) — Google requires FAQ markup to reflect on-page content. Piloted on `4.1.3`, `6.1.1`, `9.1.1`.

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
- All factual claims cited (APA 7th edition; see [`docs/references/citation-guidelines.md`](docs/references/citation-guidelines.md))
- Use the v2 custom MDX components, not raw HTML, for admonitions / figures / exercises / dropdowns
- Every Core Concept should have at least one `<Figure>`

### Exercise Scaffolding (Execute → Modify → Create)
- **Exercise 1 (Execute)**: complete runnable script, 3-5 min, reflection questions with `<Dropdown>` answers
- **Exercise 2 (Modify)**: 2-5 labeled parameters (CONFIG section or inline edit zones), 8-12 min, numbered Goals each with "What to expect" dropdown
- **Exercise 3 (Create)**: 60-85% complete starter, 3-6 TODOs with what + why, 10-15 min, progressive hint Dropdowns + final solution Dropdown, "Make It Your Own" section
- Full details: [`docs/references/scaffolding-rules.md`](docs/references/scaffolding-rules.md)

### Duration Targets
- **Modules 0-6**: 15-20 minutes maximum (target: 18 min avg)
- **Modules 7-15**: 30-45 minutes maximum (target: 40 min avg)
- **Cognitive load**: ≤ 3-4 new concepts per lesson, ≤ 5 code blocks per `## h2` section
- Full details: [`docs/references/duration-guidelines.md`](docs/references/duration-guidelines.md)

### Citations
- **Modules 0-6**: 5-7 citations minimum (APA 7th edition)
- **Modules 7-15**: 7-10 citations minimum
- Rendered in MDX as a numbered list inside `<section class="refs"><ol><li>...</li></ol></section>`
- Full details: [`docs/references/citation-guidelines.md`](docs/references/citation-guidelines.md)

### Visuals
- Every image must serve a pedagogical purpose
- Output images: < 500 KB, PNG for static, GIF for animations
- Animated diagrams: 700×380px, 15 FPS, < 500 KB
- Include `alt=` and `caption=` on every `<Figure>`
- Full details: [`docs/references/visual-guidelines.md`](docs/references/visual-guidelines.md)

---

## Asset Migration (v1 → public/lesson-media/)

[`scripts/copy-v1-assets.mjs`](scripts/copy-v1-assets.mjs) copies PNG / GIF / JPG / SVG / PY / TXT (and opt-in PTH) from v1 lesson folders into `public/lesson-media/<same v1-relative path>/`. It is driven by [`docs/reports/migration-inventory.json`](docs/reports/migration-inventory.json) (regenerate with `node scripts/migration/inventory-v1.mjs`). It:

- Treats v1 as **read-only**
- Is **idempotent** — re-running overwrites destination files
- Deliberately **skips `README.rst`** (the MDX hand-port is canonical)
- Skips subdirectories unless the lesson opts in via the `PER_LESSON` map (e.g. `visuals/`)

```powershell
npm run copy-assets                       # all lessons in the inventory
npm run copy-assets -- --only=4.1.2       # one lesson
```

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
npm install          # one-time
npm run dev          # dev server (http://localhost:4321)
npm run check        # lesson wiring + asset integrity (gates build)
npm run status       # per-module shipped/total progress table
npm run build        # check + production build to dist/
npm run preview      # serve the production build
npm run copy-assets  # pull a lesson's media from v1
```

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
10. **Ship a lesson in two steps** — drop the MDX, then add the `lessonSlug` to `src/data/curriculum/subtopics.ts`
11. **Lesson URLs are stable** — `/lessons/<id>` never changes; renaming or moving an MDX file must preserve the numeric filename prefix that `generateId` extracts

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

For detailed guidelines, read these files in [`docs/references/`](docs/references/):

| Document | Contents |
|----------|----------|
| [`scaffolding-rules.md`](docs/references/scaffolding-rules.md) | Execute / Modify / Create pass criteria, red flags, CONFIG vs inline edit zones |
| [`duration-guidelines.md`](docs/references/duration-guidelines.md) | Duration estimation formulas, cognitive load limits, trimming guidelines |
| [`citation-guidelines.md`](docs/references/citation-guidelines.md) | APA 7th edition formats, MDX rendering, quality checklist |
| [`visual-guidelines.md`](docs/references/visual-guidelines.md) | When to create visuals, technical requirements, `<Figure>` embedding |
| [`ai-revision-framework.md`](docs/references/ai-revision-framework.md) | AI pattern detection taxonomy, risk levels, transformation techniques |

Curriculum structure (module/framework table) and the thesis research context: [`docs/curriculum.md`](docs/curriculum.md).

---

## Troubleshooting

**`npm run check` fails** — read the error lines; it pinpoints the exact missing MDX, missing asset, legacy `/lessons/<id>/<file>` asset path, or duplicate slug.

**MDX schema error on `npm run build`** — open `src/content/config.ts` and check the failing field against the Zod schema. Common: `framework` value not in the enum, missing required `title` or `objective`.

**`<Figure>` shows broken image** — the asset is missing under `public/lesson-media/…`. Re-run `npm run copy-assets -- --only=<id>` or copy the file in manually (`npm run check` lists the exact path).

**Dev server doesn't pick up a new lesson** — Astro caches `src/content/lessons/`. Restart `npm run dev`.

**`tsc` complains about an MDX import** — make sure the lesson is referenced through Content Collections (`getCollection('lessons')`), not directly. See `src/pages/lessons/[slug].astro`.

**v1 Python script fails in v1 venv** — v1 is read-only. Document the failure in the port log; port the existing output PNG and either skip the broken example or write a v2-side replacement script under the lesson's `public/lesson-media/…/` folder.

**Lesson card still says "Coming soon" after dropping the MDX** — you missed step 2 of the ship workflow. Add `lessonSlug: '<id>'` to the matching leaf in `src/data/curriculum/subtopics.ts`.

---

*Adapted from v1 CLAUDE.md (numpy-to-genAI) with stack and workflow rewritten for v2. The pedagogy, quality standards, and research framing are unchanged — only the surface (Astro/MDX vs Sphinx/RST) is different.*
