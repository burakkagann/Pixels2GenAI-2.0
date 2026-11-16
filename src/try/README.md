# /try: the free sample lesson

Public mode of the workshop lesson player. Source of the copied files: `workshop-area` at c901d51.

Copied unchanged: `src/lib/workshop/{cells,cell-result,editor,friendly-errors,outputs,pixel-window,pixel-window-math,progress,unlock}, and `lesson.ts` except its last line`,
`public/runner/cell-worker.mjs`, `src/styles/workshop-lesson{,-b}.css`, and the components `MakeItFirst`, `Step`, `Task`, `Hint`, `Preview` in
`src/components/workshop-lesson/`. Changed for public mode: `Cell.astro` (reads `src/try/cells/` through a `folder` prop) and `Screen.astro`
(no tutor button or panel on `/try`; one line instead) and the last line of `lesson.ts` (no Python warm-up on page load when `data-public` is set: the privacy page says Python loads only after a click on Run). `Base.astro` gained the `focus` prop.

- `cells/` holds the code and the answer checks (build time only, never copied to the site). Test: `npm run test:try`.
- `public/try-media/` holds what the browser fetches: `helpers.py`, the photo and the figures. No `.check.py` there.
- At merge with `workshop-area` (BLD-15): keep the workshop-area copies, delete the duplicates, keep `Screen.astro` and `Cell.astro` changes.


Privacy (16 Nov): in public mode the outputs row keeps images in memory only (`createOutputsRow(..., keepInBrowser = !data-public)` in `outputs.ts`, one argument in `lesson.ts`). Both differ from the workshop-area copies; keep the workshop-area behaviour at merge.
