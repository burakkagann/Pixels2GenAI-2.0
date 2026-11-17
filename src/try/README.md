# /try: the free sample lesson

Public mode of the workshop lesson player. Source of the copied files: `workshop-area` at c901d51.

Copied unchanged: `src/lib/workshop/{cells,cell-result,editor,friendly-errors,outputs,pixel-window,pixel-window-math,progress,unlock}, and `lesson.ts` except its last line`,
`public/runner/cell-worker.mjs`, `src/styles/workshop-lesson{,-b}.css`, and the components `MakeItFirst`, `Step`, `Task`, `Hint`, `Preview` in
`src/components/workshop-lesson/`. Changed for public mode: `Cell.astro` (reads `src/try/cells/` through a `folder` prop) and `Screen.astro`
(no tutor button or panel on `/try`; the tutor is named once, in the done box) and the last line of `lesson.ts` (no Python warm-up on page load when `data-public` is set: the privacy page says Python loads only after a click on Run). `Base.astro` gained the `focus` prop.

TF-3 + HA-1 (16 Nov 2026): copied from workshop-area c901d51 `Theory.astro` and `TheoryList.astro` (unchanged then; `TheoryList` gained a `<slot />` for the concept rows on 16 Nov, see below), and `Diagram.astro`
with two public-mode props (`folder`, a folder under public/; `phoneHeight`, a stacked 800 px drawing for screens up to 600 px).
`Screen.astro` no longer shows the tutor line (the tutor is named once, in the done box). `lesson.ts` reads the done link label
from `data-done-link` (the player says "Back to the arc"). `TryWrap.astro` is the Wrap up screen; `TryDone.astro` is the last screen, the done box alone (16 Nov test run).

- `figures.py` draws the four figures into `public/try-media/fig/` (light, dark, wide and phone): `python src/try/figures.py`.
- `cells/` holds the code and the answer checks (build time only, never copied to the site). Test: `npm run test:try`.
- `public/try-media/` holds what the browser fetches: `helpers.py`, the photo and the figures. No `.check.py` there.
- At merge with `workshop-area` (BLD-15): keep the workshop-area copies, delete the duplicates, keep the `Screen.astro`, `Cell.astro`, `Diagram.astro` and `lesson.ts` (done link) changes.


Privacy (16 Nov): in public mode the outputs row keeps images in memory only (`createOutputsRow(..., keepInBrowser = !data-public)` in `outputs.ts`, one argument in `lesson.ts`). Both differ from the workshop-area copies; keep the workshop-area behaviour at merge.

Progress (16 Nov, PRV-1 a): `progress.js` `KEY_RE` now also accepts `try/<slug>` so /try screen progress is saved under `p2g-ws-progress-v1` (it was dropped before). One regex line; carry it to the workshop-area copy at merge.

## Concept framework (TT-A + FW-1 to FW-6, 16 Nov 2026; build plan R-6a8a-35)

/try runs 9 screens (per-screen minutes sum to 15, see Minutes below): Make it first, then concept, step, concept, step, concept, step, then Wrap up
(recall, the three lines, theory list, credit, Sources), then the done screen (`TryDone.astro`: the done box only, no minutes).

- Concept library: `src/content/concepts/<id>.mdx` (collection `concepts` in `src/content/config.ts`), body = Explain
  (≤ 70 words). Figures for public pages in `public/concepts/fig/` (grid-zoom, mask, three-bands, dom-grey.png, drawn
  by `figures.py`); gated concepts put theirs in `workshop-media/concepts/` (TRB-3 a). `dom-shares.json` holds the
  slider's ink share per threshold, from the lesson's rule on the full photo.
- Rules: `src/lib/concepts/rules.mjs`, run by `scripts/check-concepts.mjs` (in `npm run check` and `npm run build`)
  and thrown by the components. Tests: `npm run test:concepts` (one in-memory fixture per rule). The check script
  parses frontmatter with `js-yaml` (installed with Astro, not a direct dependency).
- New files (no workshop-area copies, so no merge conflict): `ConceptScreen`, `ConceptFigure`, `ConceptLink`,
  `ConceptRows`, `Predict`, `Recall`, `ThresholdExplorer` in `src/components/workshop-lesson/`,
  `src/lib/workshop/concepts.ts`, `src/styles/concepts.css`.
- Shared edits to carry at the BLD-15 merge (P-2): `lesson.ts` (dispatches `wb:screen` after each screen change and
  listens for `wb:go`; two lines plus comments), `TheoryList.astro` (a `<slot />` for the concept rows),
  `src/content/config.ts` (the `concepts` collection), `package.json` (`check`, `build`, `test:concepts`).
- `one-rule` figure dropped (the slider shows the idea); `three-bands` moved to `public/concepts/fig/`.
- Ink shares checked against `figures.py` with the lesson's rule (light = (r + g + b) / 3, light < t): 18.5 % at 60,
  34.6 % at 120, shown as 19 % and 35 %. The plan's 18 % came from rounded brightness values.
- Phone line numbers (R-6a8a-32 open item): a capture effect. CodeMirror measures an editor when it scrolls into
  view; off-screen in a full-page capture the numbers sit 52 px off, in view they line up (0 px, 360 / 390 / 768).

## Citations (CT-2, 16 Nov 2026)

- `Cite.astro` (marker: `<Cite c="Gonzalez & Woods, 2018" />`), `src/lib/workshop/cite.ts` (runtime, `startCites(root)`, started in
  `TryLesson.astro`), `src/styles/cite.css`. New files, no workshop-area copies. A marker shows `[n]`, n = the place of its entry in the
  lesson's one Sources list on Wrap up (`<ol data-sources="">` inside the "Sources (n)" fold). Same numbering on every screen; the list is the only list.
- Card: hover (150 ms), Tab focus, click / Enter (stays open), tap (bottom sheet with Close when there is no hover or the window is 640 px or less).
  Escape, an outside click, a scroll, a resize or a screen change close it. Marker = `<button>` with the name "Source n: Name, year".
- Data shape unchanged: concept files keep `cite: ["Name & Name, 2018"]`; the body now holds `<Cite c="..." />` where the text had "(Name, 2018)".
  `ConceptScreen` and `ConceptRows` pass `Cite` to `<Content components>`; a lesson gets it through the components map in `try.astro`.
- New rules in `rules.mjs` (tests in `check-concepts.test.mjs`): every cite has a marker, no marker without a cite, no bracketed form, a lesson
  `<Cite>` needs its Sources entry, exactly one `data-sources` list and it sits in Wrap up, the "Sources (n)" count matches.
- Merge: add `startCites(root)` next to `startConcepts` in the player page; the Sources fold is a plain `Hint kind="note"`.

## Notes on a step (SN-1, 16 Nov 2026)

- The step panel "Theory for step n" is now "Notes for step n": (a) Concept (CL b, 16 Nov): the `ConceptLink`, first row of the panel via the new `concept` slot of `Screen.astro` (a panel with only this row still shows; strip reads "Notes: concept"), (b) `Watch out`: at most
  one code detail, `<Theory slot="theory" title="Watch out" line="...">`, shown before running; (c) `Why it worked`: `<Theory slot="after" ...>`, locked
  until the step's check passes. No theory in the panel: it lives on the concept screens.
- `Screen.astro` also gained the `concept` named slot (merge: keep it; `concepts.ts` return focus falls back to the strip). `Screen.astro` gained the `notes` prop (set by `TryStep.astro`): labels only; `lesson.ts` is unchanged. `concepts.css` hides the part's own
  heading inside the panel (the row label says it). Wrap up list labels: "watch out: ...", "why it worked: ...".
- Rules (public lessons): at most one Watch out and one Why it worked per step, exact titles, each names a code line, Why it worked needs a `check` cell, no note in another slot.
- At merge: keep the `notes` prop on the workshop-area `Screen.astro`; workshop lessons keep the Theory labels until P-2 moves them.

## Concept row (CR-2, 16 Nov 2026)

- The Concept row of "Notes for step n" shows a 72 px thumbnail of the concept's figure (light and dark, with its alt text; the
  threshold concept, whose screen has the slider, shows its static `mask` figure), the title, the key idea and "Open the concept ↗"
  (opens the concept screen; "Back to step n" there returns). Built in `ConceptLink.astro` (`inPanel`), styles in `concepts.css`
  (`.wb-concept-card`); `ConceptFigure` gained an `alt` prop for thumbs.
- `keyIdea` (concept frontmatter, required): one sentence, at most 20 words, never a step's code answer. Reused in the Wrap up
  theory list (`ConceptRows`, under the title) and in "Earlier: <short> (<label>) ↗" links. Rules in `rules.mjs` (required,
  one sentence, ≤ 20 words), tests in `check-concepts.test.mjs`.

## Minutes (16 Nov 2026)

The /workshops Try card and caption, the /workshops series row and the page description say 15 minutes (Kağan's pick). Kağan's test run (16 Nov):
"it takes almost 15 min". The screens sum to 15: 2 + 1 + 3 + 1 + 2 + 1 + 3 + 2 (the 19 scaled down, largest remainder); `check-concepts.mjs`
holds /try to a 15-minute budget.

## Test run notes (16 Nov 2026)

- Recall questions rewritten: each needs the idea (unequal channels, the strict `<`, the first `True` wins) and differs from its prediction (rule).
- Wrap up is recall only: the own-words task is gone (TRB-2; rule: no `<Task>` in Wrap up).
- The done box is its own last screen (`TryDone.astro`, phase `wrap`, so `lesson.ts` fills it unchanged). The phone bar hides Run on Wrap up
  and the done screen, and Next on the last screen (`try.css`).
