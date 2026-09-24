# Retrieval results (2026-09-23)

Chunks: 640. Model: bge-small-en-v1.5. Hit@k = gold chunk in the top k; MRR averaged over answerable questions (depth 10).

## Set Q dev

| Setup | hit@1 | hit@3 | MRR | lesson@3 | hit@3 on-page | hit@3 off-page |
|---|---|---|---|---|---|---|
| BM25 | 29% | 51% | 0.43 | 69% | 50% (n=30) | 60% (n=5) |
| Dense | 31% | 43% | 0.39 | 54% | 37% (n=30) | 80% (n=5) |
| Hybrid (RRF) | 31% | 66% | 0.48 | 74% | 60% (n=30) | 100% (n=5) |
| Hybrid + boost 0.005 (day 5) | 49% | 71% | 0.62 | 80% | 67% (n=30) | 100% (n=5) |
| Hybrid + boost 0.01 (chosen on dev) | 54% | 77% | 0.69 | 86% | 73% (n=30) | 100% (n=5) |
| Hybrid + large boost | 54% | 80% | 0.69 | 89% | 90% (n=30) | 20% (n=5) |

## Set Q test

| Setup | hit@1 | hit@3 | MRR | lesson@3 | hit@3 on-page | hit@3 off-page |
|---|---|---|---|---|---|---|
| BM25 | 42% | 74% | 0.57 | 77% | 65% (n=23) | 100% (n=8) |
| Dense | 35% | 55% | 0.46 | 65% | 43% (n=23) | 88% (n=8) |
| Hybrid (RRF) | 58% | 74% | 0.66 | 77% | 70% (n=23) | 88% (n=8) |
| Hybrid + boost 0.005 (day 5) | 61% | 81% | 0.71 | 90% | 78% (n=23) | 88% (n=8) |
| Hybrid + boost 0.01 (chosen on dev) | 68% | 81% | 0.76 | 90% | 83% (n=23) | 75% (n=8) |
| Hybrid + large boost | 55% | 68% | 0.63 | 74% | 91% (n=23) | 0% (n=8) |

## Set R

| Setup | hit@1 | hit@3 | MRR | lesson@3 | hit@3 on-page | hit@3 off-page |
|---|---|---|---|---|---|---|
| BM25 | 22% | 28% | 0.29 | 44% | 28% (n=18) | n/a |
| Dense | 22% | 44% | 0.34 | 50% | 44% (n=18) | n/a |
| Hybrid (RRF) | 11% | 44% | 0.29 | 61% | 44% (n=18) | n/a |
| Hybrid + boost 0.005 (day 5) | 28% | 61% | 0.47 | 72% | 61% (n=18) | n/a |
| Hybrid + boost 0.01 (chosen on dev) | 39% | 67% | 0.57 | 83% | 67% (n=18) | n/a |
| Hybrid + large boost | 39% | 89% | 0.66 | 100% | 89% (n=18) | n/a |

## Set T

| Setup | hit@1 | hit@3 | MRR | lesson@3 | hit@3 on-page | hit@3 off-page |
|---|---|---|---|---|---|---|
| BM25 | 40% | 55% | 0.49 | 75% | 62% (n=16) | 25% (n=4) |
| Dense | 35% | 50% | 0.44 | 95% | 56% (n=16) | 25% (n=4) |
| Hybrid (RRF) | 35% | 60% | 0.51 | 100% | 62% (n=16) | 50% (n=4) |
| Hybrid + boost 0.005 (day 5) | 45% | 60% | 0.58 | 100% | 62% (n=16) | 50% (n=4) |
| Hybrid + boost 0.01 (chosen on dev) | 45% | 70% | 0.60 | 100% | 75% (n=16) | 50% (n=4) |
| Hybrid + large boost | 40% | 65% | 0.55 | 90% | 75% (n=16) | 25% (n=4) |

## Unanswerable detection (best cosine score)

- Answerable questions: min 0.569, 10th percentile 0.640, median 0.715
- Unanswerable questions: Q62 0.741, Q59 0.740, Q57 0.712, R06 0.696, Q58 0.684, Q60 0.671, Q61 0.573
- A threshold just above the highest unanswerable score (0.741) would also reject 73 of 104 answerable questions.
