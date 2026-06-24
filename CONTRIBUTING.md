# Contributing to Pixels2GenAI

Thanks for your interest in helping build Pixels2GenAI. This is an open
educational curriculum, and the single most valuable contribution is **porting a
lesson** — taking one of the ~190 unshipped exercises and bringing it to life as
a polished MDX lesson.

By contributing you agree that your code is licensed under [MIT](LICENSE) and
your curriculum content under [CC-BY 4.0](LICENSE-CONTENT.md).

## Ways to contribute

- **Port a lesson** *(primary)* — turn an unshipped leaf into an MDX lesson.
- **Improve a shipped lesson** — clarity, accuracy, better visuals, citations.
- **Fix a bug** — broken links, layout issues, build problems.
- **Propose an exhibition concept** — cross-module generative art pieces.

If you're unsure where to start, run `npm run status` to see which modules are
empty, or open a *Lesson contribution* issue to claim a leaf before you begin.

## Tech stack

- **[Astro 5](https://astro.build)** — static output, zero JS by default
- **React 19** — a single client island (the 3D Journey Cube hero)
- **MDX** — lesson content authored with a custom component kit
- **TypeScript** (strict)
- **Vanilla CSS** with design tokens (CSS custom properties, OKLCH-derived palette)
- Build-time **Open Graph images** ([astro-og-canvas](https://github.com/delucis/astro-og-canvas)) and **sitemap** ([@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/))

## Development setup

Requires **Node 20** (see [`.nvmrc`](.nvmrc)).

```bash
git clone https://github.com/burakkagann/Pixels2GenAI-2.0.git
cd Pixels2GenAI-2.0
npm install        # Node 20 — see .nvmrc
npm run dev        # http://localhost:4321
```

That's all you need to browse and edit the site. When porting a lesson, you also
pull its media from the v1 archive with `npm run copy-assets` (see below).

### Scripts

| Script | What it does |
|--------|--------------|
| `npm run dev` | Astro dev server at `localhost:4321` |
| `npm run build` | Runs the lesson integrity check, then builds to `dist/` |
| `npm run build:nocheck` | Build without the pre-flight check (escape hatch) |
| `npm run preview` | Serve the production build locally |
| `npm run check` | Validate lesson wiring — `lessonSlug` ↔ MDX, assets, duplicate slugs (gates `build`) |
| `npm run status` | Per-module shipped/total progress table |
| `npm run copy-assets` | Copy a lesson's assets from the v1 repo into `public/lesson-media/` |
| `npm run gen-icons` | Regenerate favicons / touch icons |

### Project layout

```
.
├── astro.config.mjs          Astro config (site URL, sitemap, MDX, remark plugin)
├── netlify.toml              Netlify build settings
├── docs/                     contributor docs — quality references, generated reports
├── public/
│   ├── lesson-media/         per-lesson media (PNG / GIF / .py / .pth),
│   │                         mirrors src/content/lessons/ folder for folder
│   ├── exhibitions/          exhibition poster + print images
│   └── workshops/            workshop posters + gallery
├── scripts/
│   ├── check-lessons.mjs     lesson integrity check (npm run check)
│   ├── lesson-status.mjs     progress report (npm run status)
│   ├── copy-v1-assets.mjs    v1 → public/lesson-media asset migrator
│   ├── lib/catalog.mjs       shared catalog reader for the tooling
│   └── migration/            archived one-shot migration scripts
├── src/
│   ├── pages/                routes — index, lessons/[slug], research, workshops,
│   │                         exhibitions/2026-03, imprint, 404, og/[...route]
│   ├── layouts/              Base, Lesson, Research
│   ├── content/
│   │   ├── config.ts         glob loader (slug = numeric id) + Zod schema
│   │   └── lessons/          lesson MDX, mirrors v1's content/ hierarchy:
│   │                         Module_xx_…/x.y_…/x.y.z_<name>.mdx
│   ├── components/
│   │   ├── chrome/           top frame, footer, grain overlay
│   │   ├── cube/             React-island JourneyCube
│   │   ├── lesson/           lesson chrome + mdx/ component kit
│   │   ├── exhibitions/      exhibition specimen + layout
│   │   ├── workshops/        workshop specimen + signup form
│   │   └── research/         research-page sections
│   ├── data/
│   │   ├── curriculum/       modules.ts + subtopics.ts (source of truth)
│   │   └── site/             research.ts, exhibitions.ts, workshops.ts
│   ├── lib/                  cube color pipeline + GitHub star badge
│   └── styles/               global CSS (tokens, base, typography, prose)
└── CLAUDE.md                 contributor + automation guide
```

### Site map

| Route | Page |
|-------|------|
| `/` | Landing — Journey Cube, curriculum, workshops, exhibition, research |
| `/lessons/<slug>` | A lesson (e.g. `/lessons/1.1.1`) |
| `/research` | Thesis / research overview |
| `/workshops` | Workshop archive + signup |
| `/exhibitions/2026-03` | Berlin exhibition (March 2026) |
| `/imprint` | Legal imprint |

## Porting a lesson

A lesson is **shipped** — i.e. appears as a clickable card on the site — when
**both** of these are in place:

1. **The MDX file** at `src/content/lessons/<lesson-path>.mdx`, valid against the Zod
   schema in [`src/content/config.ts`](src/content/config.ts), with assets under
   `public/lesson-media/<lesson-path>/`.
2. **`lessonSlug: '<slug>'`** added to the matching leaf in
   [`src/data/curriculum/subtopics.ts`](src/data/curriculum/subtopics.ts). If it's the module's first
   ported lesson, also set `firstLesson` in
   [`src/data/curriculum/modules.ts`](src/data/curriculum/modules.ts).

Until step 2, the leaf renders dim as "Coming soon" and is unreachable.

### The workflow

Source prose and Python come from the **v1 archive** (`numpy-to-genAI`), which is
**read-only** — never modify it; work around bugs on the v2 side and note them.

1. **Copy assets** — add your lesson to the `LESSONS` array in
   [`scripts/copy-v1-assets.mjs`](scripts/copy-v1-assets.mjs), then
   `npm run copy-assets`.
2. **Hand-port the MDX** — write `src/content/lessons/<lesson-path>.mdx` using the
   component kit in [`src/components/lesson/mdx/`](src/components/lesson/mdx/):
   `Admonition`, `CodeBlock`, `Download`, `Dropdown`, `Exercise`, `Figure`.
   Use these instead of raw HTML.
3. **Validate** — `npm run check` (and `npm run build`) must pass.
4. **Wire it up** — add the `lessonSlug` (and `firstLesson` if first).

If you use Claude Code, the repo ships skills that automate this pipeline:
`lesson-port` → `exercise-testing` → `ai-revision` (see
[`.claude/skills/`](.claude/skills/)).

## Quality bar

These are non-negotiable; details live in
[`docs/references/`](docs/references/):

- **Scaffolding** — every exercise set follows *Execute → Modify → Create*
  (`scaffolding-rules.md`).
- **Duration** — 15–20 min for modules 0–6, 30–45 min for 7–15; ≤ 3–4 new
  concepts per lesson (`duration-guidelines.md`).
- **Citations** — every factual claim cited, APA 7th edition; 5–7 (modules 0–6)
  or 7–10 (modules 7–15) references (`citation-guidelines.md`).
- **Visuals** — every image serves a purpose, has `alt=` and `caption=`,
  output < 500 KB (`visual-guidelines.md`).
- **Tone** — academic yet friendly. **No emojis** in lesson MDX or downloadable
  scripts.
- **Code** — runs on Python 3.11; clarity over cleverness; humanized variable
  names; comments explain *why*. Author downloadable scripts as
  **"Pixels2GenAI Project"** — never "Claude".

## Before you open a PR

```bash
npm run check     # must pass — validates slug↔MDX wiring and assets
npm run build     # must succeed
npm run status    # sanity-check your lesson now shows as shipped
```

- Branch from `main`.
- Write clear, descriptive commit messages.
- Fill out the PR template; reference the issue/leaf you're addressing.
- Keep PRs focused — one lesson (or one fix) per PR where possible.

## Deploy

The live site is hosted on **Netlify**, which rebuilds on every push to `main`:

- Build command: `npm run build` → output `dist/` (see [`netlify.toml`](netlify.toml))
- Node 20
- `site` is set to `https://pixels2genai.art` in [`astro.config.mjs`](astro.config.mjs)

Note: OG-image generation fetches its fonts at build time, so the build needs
network access (available on Netlify).

## Reporting bugs

Open a *Bug report* issue with the page URL, what you expected, what happened,
your browser/OS, and a screenshot if it's visual.

---

Questions? Open an issue or reach the maintainer via the contact link in the
site footer. Thank you for contributing.
