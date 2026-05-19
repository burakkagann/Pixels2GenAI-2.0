# Pixels2GenAI v2 — Risograph Edition

The next-generation site for the Pixels to GenAI curriculum, built around a new Risograph visual language (riso violet primary + fluoro pink studio ink on a violet-tinted near-black base) and a 3D Journey Cube hero. Separate deployment from the legacy v1 (Sphinx, `numpy-to-genAI`), which remains live as the archived reference.

**Status**: scaffold + 3 sample lessons (1.1.1, 4.1.1, 12.1.2). Bulk lesson migration is deferred.

## Stack

- Astro 5 (static output, zero JS by default)
- React 19 (single island: the Journey Cube)
- MDX (lesson content with custom components)
- TypeScript strict
- Vanilla CSS with Nocturne tokens (CSS custom properties)

## Develop

```bash
npm install
npm run copy-assets   # one-time: pulls lesson PNGs / GIFs / scripts / weights from v1
npm run dev           # http://localhost:4321
```

## Build

```bash
npm run build         # output in dist/
npm run preview       # serve dist/ locally
```

## Deploy (Netlify)

This folder is intended to live in its own git repo, not inside `numpy-to-genAI/`. Move it out before deploying:

```bash
mv ../Pixels2GenAI-v2 ~/projects/pixels2genai-v2
cd ~/projects/pixels2genai-v2
git init && git add . && git commit -m "Initial scaffold"
# Push to a new GitHub repo, then connect to Netlify.
```

`netlify.toml` is already configured (`npm run build` → `dist/`, Node 20). Domain target: `pixels2genai.art`.

## Project layout

```
src/
├── styles/              global CSS (tokens, base, typography, prose)
├── lib/                 cube color pipeline (OKLCH → sRGB LUTs) + pattern fns
├── components/
│   ├── chrome/          top frame, footer, grain overlay
│   ├── cube/            React-island JourneyCube + controls
│   ├── landing/         landing-page sections
│   └── lesson/          lesson-page chrome + MDX components
├── layouts/             Base, Lesson
├── content/             Content Collections (lessons, modules)
└── pages/               routes (index, lessons/[slug], 404)
public/lessons/          copied v1 assets (NOT in git for the model weights file)
scripts/copy-v1-assets.mjs   one-shot asset migrator
```

## What's intentionally not here yet

- 144 of 147 lessons (only 1.1.1, 4.1.1, 12.1.2 ported)
- Search, sitemap, analytics
- Editorial / Notebook lesson variants (Documentation variant only)
- Cube tweaks panel (theme / scale / read-width toggles)

These are scheduled for post-scaffold iterations. See `..\.claude\plans\floofy-rolling-squirrel.md` for the full plan.

## Legacy edition

v1 (Sphinx) is frozen but live: <https://burakkagann.github.io/numpy-to-genAI>
