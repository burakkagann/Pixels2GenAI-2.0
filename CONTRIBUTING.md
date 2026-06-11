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

## Development setup

```bash
git clone https://github.com/burakkagann/Pixels2GenAI-2.0.git
cd Pixels2GenAI-2.0
npm install        # Node 20 — see .nvmrc
npm run dev        # http://localhost:4321
```

## Porting a lesson

A lesson is **shipped** — i.e. appears as a clickable card on the site — when
**both** of these are in place:

1. **The MDX file** at `src/content/lessons/<slug>.mdx`, valid against the Zod
   schema in [`src/content/config.ts`](src/content/config.ts), with assets under
   `public/lessons/<slug>/`.
2. **`lessonSlug: '<slug>'`** added to the matching leaf in
   [`src/data/subtopics.ts`](src/data/subtopics.ts). If it's the module's first
   ported lesson, also set `firstLesson` in
   [`src/data/modules.ts`](src/data/modules.ts).

Until step 2, the leaf renders dim as "Coming soon" and is unreachable.

### The workflow

Source prose and Python come from the **v1 archive** (`numpy-to-genAI`), which is
**read-only** — never modify it; work around bugs on the v2 side and note them.

1. **Copy assets** — add your lesson to the `LESSONS` array in
   [`scripts/copy-v1-assets.mjs`](scripts/copy-v1-assets.mjs), then
   `npm run copy-assets`.
2. **Hand-port the MDX** — write `src/content/lessons/<slug>.mdx` using the
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
[`thesis_automation/references/`](thesis_automation/references/):

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

## Reporting bugs

Open a *Bug report* issue with the page URL, what you expected, what happened,
your browser/OS, and a screenshot if it's visual.

---

Questions? Open an issue or reach the maintainer via the contact link in the
site footer. Thank you for contributing.
