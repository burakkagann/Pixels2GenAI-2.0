# Eval question sets

One question per line (JSON Lines). Each `gold` lists the chunk ids (from `ai-tutor/data/chunks.json`) that count as a correct retrieval; an empty `gold` means the question is not answerable from the shipped lessons.

| File | What it is | Provenance | Size |
|---|---|---|---|
| `set_r.jsonl` | Real learner confusions from the February 2026 workshop exit tickets (thesis Table B.6) | `source_quote` is verbatim; `question` is a minimal rephrasing into a question; module-only attribution, no participant codes | 19 |
| `set_q.jsonl` | Curriculum questions across 20 lessons and every shipped module | **Model-written** (Claude, 2026-09-23), including the curriculum-specific questions; gold labels checked against `chunks.json`; author review pending | 72 |

Validate after any edit: `python ai-tutor/evals/check_sets.py` (add `--list <lesson id>` to see a lesson's gold ids).

| `set_t.jsonl` | **Bias check:** questions written by an independent agent from lesson titles and objectives only, before it read any lesson text | Model-written, single-rater gold (the same agent labelled them after writing) | 20 |

## Label quality (2026-09-23)

- Gold for sets Q and R was labelled twice: by the question author and, blind, by an independent agent that never saw the first labels. Agreement over 91 questions: answerable-vs-not 99%, at least one shared section 99%, the second rater's top pick inside the first rater's gold 92%.
- Final gold is the **union** of both raters' sections (any section that genuinely answers counts), with `kind` recomputed from it; 6 questions first marked off-page turned out to be answerable on their own page. The only real disagreement (R06, a general "how do I read code" question) stays unanswerable.
- **Caveat:** both raters are Claude models, so they share blind spots; the agreement rules out careless errors, not systematic ones. A human spot-check (author or supervisor) is still needed before results are published.
- Set Q is split once into `dev` (38) and `test` (34) with a fixed seed, stratified by kind and style. Settings are chosen on dev only; test is what gets reported.

## Fields

- `asked_on`: the lesson page the learner is on when asking (drives the current-lesson boost).
- `kind`: `on_page` (answer is on `asked_on`), `off_page` (answer is in another lesson), `unanswerable`.
- `style` (set Q): `everyday` (learner's own words), `identifier` (names a function or term, e.g. `np.kron`), `curriculum_specific` (the lesson's answer is more specific than general knowledge).
- `closest`: for an unanswerable question, the section the tutor should point to instead, if any.

## Known limitations (report these with the results)

- **Set Q is model-written.** Its wording may lean towards the lessons' own vocabulary, which would make retrieval look better than it is on real learner questions. Compare set Q results with set R; a large gap is a sign of this bias.
- **The bias is real and measured:** on the title-only set T, the best setup scores 60% hit@3 against 81% on set Q test, and real learners (set R) score 61%. Quote the set R / set T level as the realistic estimate, not set Q.
- **Set Q mix (72), after the label merge:** 53 on-page, 13 off-page, 6 unanswerable; 49 everyday, 6 identifier, 11 curriculum-specific (plus the 6 unanswerable). Off-page questions are now scarce (5 in dev), so a setting chosen on overall dev score will over-reward the current-lesson boost; judge boosts on on-page and off-page separately.
- **Small sets:** in set Q one question is ~1.5 percentage points, in set R ~5; treat differences under ~5 points (set Q) as noise.
- **Gold labels are one person's judgement**, and several questions have more than one acceptable section.

## Known limitations (report these with the results)

- **Set Q is model-written.** Its wording may lean towards the lessons' own vocabulary, which would make retrieval look better than it is on real learner questions. Compare set Q results with set R; a large gap is a sign of this bias.
- **Set Q mix:** 40 on-page, 16 off-page (29% of answerable), 6 unanswerable (10%); 49 everyday, 6 identifier, 1 curriculum-specific, 6 unanswerable.
- **60 questions is small:** one question is ~1.6 percentage points, so treat differences under ~5 points as noise.
- **Gold labels are one person's judgement**, and several questions have more than one acceptable section.
