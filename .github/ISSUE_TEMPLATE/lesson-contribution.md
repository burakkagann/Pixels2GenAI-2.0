---
name: Lesson contribution
about: Claim or propose porting / improving a lesson
title: "[Lesson] <leaf id> — <title>"
labels: ["lesson", "content"]
---

<!-- See CONTRIBUTING.md for the full porting workflow before you start. -->

## Lesson

- **Leaf id:** <!-- e.g. 1.2.2 -->
- **Module:** <!-- e.g. M 01 · Pixel Fundamentals -->
- **Proposed slug:** <!-- e.g. 1.2.2 -->

## Source

- **v1 source (numpy-to-genAI):** <!-- link or path to the RST + Python -->
- Anything notable (broken v1 script, missing assets, etc.):

## What I'm doing

- [ ] Porting a new lesson
- [ ] Improving an existing shipped lesson
- [ ] Other (describe):

## Ship checklist

- [ ] Assets copied into `public/lessons/<slug>/`
- [ ] MDX added at `src/content/lessons/<slug>.mdx` (schema-valid)
- [ ] `lessonSlug` wired into `src/data/subtopics.ts` (+ `firstLesson` if first)
- [ ] `npm run check` passes and `npm run build` succeeds
- [ ] Follows the quality bar (scaffolding, citations, no emojis)
