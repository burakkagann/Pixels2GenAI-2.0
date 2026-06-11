# Pixels2GenAI

**From a single pixel to generative AI — one continuous thread.**

An open, free curriculum that takes a learner from a single array element to
building, training, and reasoning about modern generative models, across fifteen
progressive modules. Each module produces a visual artifact.

🌐 **Live site: <https://pixels2genai.art>**

[![Live](https://img.shields.io/badge/live-pixels2genai.art-B585E8)](https://pixels2genai.art)
[![Code: MIT](https://img.shields.io/badge/code-MIT-9AC07A)](LICENSE)
[![Content: CC-BY 4.0](https://img.shields.io/badge/content-CC--BY%204.0-66B8FF)](LICENSE-CONTENT.md)
[![Built with Astro](https://img.shields.io/badge/built%20with-Astro%205-FF5D01)](https://astro.build)

---

## What it is

Pixels2GenAI is an educational platform teaching generative art and AI through a
linear, scaffolded curriculum of **15 modules + a capstone**, organised in three
design-based-research cycles (Foundations → Machine Learning → Generative AI).
It is the empirical artifact of a Master's thesis in creative computing. The
pedagogy is theory (40%) / practice (60%) with an *Execute → Modify → Create*
progression and a visual-first, immediate-feedback approach.

Read the research framing on the live site: <https://pixels2genai.art/research>.

## Status

The site and design system are live; lesson content is being ported module by
module. **3 of 193 lessons are shipped today** (`1.1.1`, `4.1.1`, `12.1.2`) —
the remaining ~190 are the main contribution opportunity.

For the current count at any time, run:

```bash
npm run status
```

## Tech stack

- **[Astro 5](https://astro.build)** — static output, zero JS by default
- **React 19** — a single client island (the 3D Journey Cube hero)
- **MDX** — lesson content authored with a custom component kit
- **TypeScript** (strict)
- **Vanilla CSS** with design tokens (CSS custom properties, OKLCH-derived palette)
- Build-time **Open Graph images** ([astro-og-canvas](https://github.com/delucis/astro-og-canvas)) and **sitemap** ([@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/))

## Quick start

Requires **Node 20** (see [`.nvmrc`](.nvmrc)).

```bash
npm install
npm run dev          # http://localhost:4321
```

That's all you need to browse and edit the site. When porting a lesson, you also
pull its media from the v1 archive:

```bash
npm run copy-assets  # copies that lesson's PNG / GIF / .py / weights into public/lessons/
```

## Scripts

| Script | What it does |
|--------|--------------|
| `npm run dev` | Astro dev server at `localhost:4321` |
| `npm run build` | Runs the lesson integrity check, then builds to `dist/` |
| `npm run build:nocheck` | Build without the pre-flight check (escape hatch) |
| `npm run preview` | Serve the production build locally |
| `npm run check` | Validate lesson wiring — `lessonSlug` ↔ MDX, assets, duplicate slugs (gates `build`) |
| `npm run status` | Per-module shipped/total progress table |
| `npm run copy-assets` | Copy a lesson's assets from the v1 repo into `public/lessons/` |
| `npm run gen-icons` | Regenerate favicons / touch icons |

## Project layout

```
.
├── astro.config.mjs          Astro config (site URL, sitemap, MDX, remark plugin)
├── netlify.toml              Netlify build settings
├── public/
│   ├── lessons/<slug>/       per-lesson media (PNG / GIF / .py / .pth)
│   ├── exhibitions/          exhibition poster + print images
│   └── workshops/            workshop posters + gallery
├── scripts/
│   ├── check-lessons.mjs     lesson integrity check (npm run check)
│   ├── lesson-status.mjs     progress report (npm run status)
│   ├── copy-v1-assets.mjs    v1 → public/lessons asset migrator
│   └── lib/catalog.mjs       shared catalog reader for the tooling
├── src/
│   ├── pages/                routes — index, lessons/[slug], research, workshops,
│   │                         exhibitions/2026-03, imprint, 404, og/[...route]
│   ├── layouts/              Base, Lesson, Research
│   ├── content/
│   │   ├── config.ts         Zod schema for lesson frontmatter
│   │   └── lessons/<slug>.mdx lesson content
│   ├── components/
│   │   ├── chrome/           top frame, footer, grain overlay
│   │   ├── cube/             React-island JourneyCube
│   │   ├── lesson/           lesson chrome + mdx/ component kit
│   │   ├── exhibitions/      exhibition specimen + layout
│   │   ├── workshops/        workshop specimen + signup form
│   │   └── research/         research-page sections
│   ├── data/                 curriculum + event catalogs (source of truth)
│   ├── lib/                  cube color pipeline + GitHub star badge
│   └── styles/               global CSS (tokens, base, typography, prose)
└── CLAUDE.md                 contributor + automation guide
```

## Site map

| Route | Page |
|-------|------|
| `/` | Landing — Journey Cube, curriculum, workshops, exhibition, research |
| `/lessons/<slug>` | A lesson (e.g. `/lessons/1.1.1`) |
| `/research` | Thesis / research overview |
| `/workshops` | Workshop archive + signup |
| `/exhibitions/2026-03` | Berlin exhibition (March 2026) |
| `/imprint` | Legal imprint |

## Contributing

Contributions are welcome — most of all, **porting lessons**. The fastest way to
help is to take an unshipped leaf and bring it to life as an MDX lesson.

A lesson ships in **two steps**: (1) drop the MDX at
`src/content/lessons/<slug>.mdx` with its assets under `public/lessons/<slug>/`,
then (2) add `lessonSlug: '<slug>'` to the matching leaf in
`src/data/subtopics.ts`. Until step 2, the lesson renders as "Coming soon."

Full workflow, quality standards, and PR checklist: **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Before opening a PR, make sure `npm run check` passes (it gates the build) and
`npm run build` succeeds.

## Deploy

Hosted on **Netlify**, which rebuilds on every push to `main`:

- Build command: `npm run build` → output `dist/` (see [`netlify.toml`](netlify.toml))
- Node 20
- `site` is set to `https://pixels2genai.art` in [`astro.config.mjs`](astro.config.mjs)

Note: OG-image generation fetches its fonts at build time, so the build needs
network access (available on Netlify).

## License

Dual-licensed by design:

- **Code** — [MIT](LICENSE)
- **Curriculum content** (lesson prose, figures, diagrams) — [CC-BY 4.0](LICENSE-CONTENT.md)

© 2026 Burak Kağan Yılmazer & Kristian Rother.

## Legacy edition (v1)

The first-generation site (Sphinx + RST) is frozen but remains live as the
archived reference and the source of truth for lesson prose and Python during
porting: <https://burakkagann.github.io/numpy-to-genAI>.
