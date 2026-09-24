# Retrieval failures (Milestone 1)

**Setup analysed:** hybrid (BM25 + bge-small embeddings, RRF) with current-lesson boost 0.01, top 3 chunks.
**Date:** 2026-09-23. **Source:** `results/misses.json` (26 questions whose gold section was not in the top 3, across sets Q, R and T).

## Summary

| Pattern | Misses | Right lesson found? | Fix to try | Where |
|---|---|---|---|---|
| A. Near miss: gold at rank 4-5 | 10 | mostly | Pass the top 5 chunks to the model, not 3 | Milestone 2 |
| B. Right lesson, wrong section (Overview / Summary / another exercise wins) | 15 (overlaps A) | yes | Top 5 (above); if still needed, an LLM reranker over the top 10 | Milestone 2 |
| C. Wrong lesson with overlapping vocabulary | 7 | no | Reranker; more off-page test questions to measure it | Milestone 2 |
| D. Vague real-learner questions | 3 | no | Tutor asks a clarifying question, and treats the current page as the default context | Milestone 2 (prompt policy) |
| E. Structural references ("Task 3", "Exercise 2") | 1 | no | Resolve exercise numbers on the current page directly, before search | Milestone 4 (hint mode) |

**Most useful single number:** passing 5 chunks instead of 3 raises the chance that the right section is in front of the model from 67% to 78% on real learner questions (set R), and from 70% to 80% on set T; 8 chunks reaches 89% / 95%.

| Set | hit@3 | hit@5 | hit@8 |
|---|---|---|---|
| Q test | 81% | 87% | 90% |
| R (real learners) | 67% | 78% | 89% |
| T (title-only) | 70% | 80% | 95% |

## A / B. Near misses and wrong section

The right lesson is in the top 3 for 15 of the 26 misses; the model would see relevant material, just not the best section. Typical winners that push the gold section down:

- **Overview and Summary chunks** (9 of the 26 top-1 results) repeat every keyword of the lesson. Down-weighting them (x0.8, x0.6, removal) was tested on dev and changed hit@3 by at most one question, which is noise, so it was **not** adopted.
- **Another exercise of the same lesson** (e.g. Q29 "what do the square brackets do in the rule?" -> 4.3.1 Exercise 1, gold is Concept 2). Exercise chunks contain reflection answers that mention the same terms.

Examples: Q05 (slicing, gold rank 4), Q67 (perception radius, gold rank 4, Overview first), Q33 (chaos, gold rank 10, Summary first), T17 (smooth noise, Overview first).

## C. Wrong lesson, overlapping vocabulary

| Question | Asked on | Got | Gold | Why |
|---|---|---|---|---|
| Q09 "why does my picture come out sideways when I swap x and y?" | 1.1.1 | 3.1.3 (distortions) | 2.1.4 / 1.1.1 | "sideways" reads as rotation to both BM25 and embeddings |
| Q23 "only the up-and-down lines" | 3.4.2 | 3.4.3 Summary (contour lines) | 3.4.2 Exercise 2 | "lines" matches the contour-lines lesson |
| Q40 "holes and gaps in the letters" | 8.3.1 | 8.3.2 Overview (Thank You text animation) | 8.3.1 Concept 2 | "letters" and "animation" match the neighbouring text lesson |
| Q72 "how long without a graphics card?" | 12.4.1 | 8.3.2 Overview | 12.4.1 Quick start | the gold is one sentence inside a code-heavy chunk |
| Q54 "just paint everywhere" | 12.4.1 | 3.2.3 (shadow compositing) | 12.4.1 Exercise 2 | "paint" and "photo" are generic |
| Q06, Q12 | | | | everyday shape words ("rectangle", "circle", "edge") shared by many Module 2-3 lessons |

These are the cases where a cross-encoder or LLM reranker is most likely to help, because it reads the question and chunk together instead of comparing separate summaries of them.

## D. Vague real-learner questions

R10 "How do I write the loop if I am a beginner?", R19 "The math functions are very unfamiliar to me", R17 "I still don't understand how to make different patterns". No retrieval setup can pick one section: the question doesn't say which loop or which math. These are real workshop questions, so the tutor must handle them: answer from the current lesson's main code and ask a short clarifying question.

## E. Structural reference

R11 "How do I do Task 3 in 'Make it your own'?" refers to the lesson's structure, not its content. Search can't match "Task 3"; the tutor should resolve it directly (current page, Exercise 3) before searching.

## Also found (not retrieval misses)

- **Unanswerable questions can't be detected by similarity score** (follow-ups #8): p5.js, NFT and k-means questions score as high as answerable ones. Needs an LLM relevance judgement in Milestone 2.
- **Boost trade-off:** raising the boost from 0.005 to 0.01 improved real-learner questions (set R hit@3 61% -> 67%) but cost one off-page question on set Q test (88% -> 75%, 1 of 8).
