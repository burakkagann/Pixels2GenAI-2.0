# Retrieval experiments (set Q dev)

35 answerable dev questions: 30 on-page, 5 off-page. One on-page question = 3%, one off-page question = 20%. Balanced = mean of on-page and off-page hit@3.

## One change at a time (boost 0.005)

| Setting | hit@3 | on-page | off-page | balanced | MRR |
|---|---|---|---|---|---|
| Baseline | 71% | 67% | 100% | 83% | 0.62 |
| Summary + overview x0.8 | 74% | 70% | 100% | 85% | 0.65 |
| Summary + overview x0.6 | 71% | 67% | 100% | 83% | 0.64 |
| Summary + overview removed | 71% | 67% | 100% | 83% | 0.64 |
| Exercises x0.8 | 71% | 67% | 100% | 83% | 0.61 |
| BM25 without solution code | 71% | 67% | 100% | 83% | 0.61 |
| BM25 prose only | 74% | 70% | 100% | 85% | 0.60 |
| Dense prose only | 69% | 67% | 80% | 73% | 0.60 |

## Boost sweep (baseline settings)

| Setting | hit@3 | on-page | off-page | balanced | MRR |
|---|---|---|---|---|---|
| boost 0.0 | 66% | 60% | 100% | 80% | 0.48 |
| boost 0.002 | 69% | 63% | 100% | 82% | 0.56 |
| boost 0.005 | 71% | 67% | 100% | 83% | 0.62 |
| boost 0.01 | 77% | 73% | 100% | 87% | 0.69 |
| boost 0.02 | 89% | 90% | 80% | 85% | 0.72 |
