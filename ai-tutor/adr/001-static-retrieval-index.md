# ADR-001: Static retrieval index with hybrid search, not Postgres + pgvector

**Status:** accepted, 2026-09-23 (Milestone 1).
**Deciders:** Pixels2GenAI Project (author), with Claude as reviewer.

## Context

The tutor answers learner questions from the shipped lessons and must cite the exact section. The first plan draft put the lesson chunks in Postgres with pgvector (Neon free tier), queried from a FastAPI service.

Facts measured in Milestone 1:
- **Corpus:** 72 shipped lessons, cut into **640 chunks** (median 215 words, largest 829) by `ai-tutor/chunker.py`.
- **Embeddings:** 640 x 384 float32 = under 1 MB (`data/embeddings-all.npy`); embedding every chunk takes ~5 minutes on a laptop CPU, once per content change.
- **Search cost:** one query is a 640 x 384 matrix-vector product (~1 ms) plus BM25 over 640 chunks.
- **Content changes** only when a lesson ships, i.e. on deploy.

## Decision

1. **The index is two static files built from the MDX:** `chunks.json` (text, anchors, metadata) and one embeddings `.npy`. The API loads them at start-up and searches in memory. No database.
2. **Hybrid retrieval:** BM25 and dense search (`BAAI/bge-small-en-v1.5`, local via fastembed/ONNX), merged with Reciprocal Rank Fusion (k = 60), plus a **current-lesson boost of 0.01** (neighbouring lessons get half).
3. **Citations use section anchors taken from the same rules Astro uses** (github-slugger, typography step included), verified against the built site on every chunker run (499 of 499 found).
4. **Local embedding model**, so learner questions never leave our server for retrieval.

## Evidence (hit@3 = the gold section is among the 3 chunks returned)

| Setup | Q test (model-written) | R (real learners) | T (title-only) |
|---|---|---|---|
| BM25 only | 74% | 28% | 55% |
| Dense only | 55% | 44% | 50% |
| Hybrid (RRF), no boost | 74% | 44% | 60% |
| **Hybrid + boost 0.01 (chosen)** | **81%** | **67%** | **70%** |
| Hybrid + boost 0.03 | 68% | 89% | 65% |

- Hybrid beats either method alone on every set.
- The boost was chosen on set Q **dev** only. Boost 0.03 wins on set R only because every set R question is asked on its own page; it drops off-page questions to 0-25% (see FAILURES.md).
- Section-weight and code-stripping variants changed dev hit@3 by at most one question (noise) and were not adopted.
- Passing 5 chunks instead of 3 raises set R from 67% to 78% and set T from 70% to 80%.
- Realistic quality is the set R / T level (~67-70% hit@3, ~78-80% hit@5), not set Q (model-written questions overstate it by ~10-20 points; `evals/README.md`).

## Alternatives considered

| Option | Why not (now) |
|---|---|
| **Postgres + pgvector (Neon)** | Built for millions of vectors and changing data; here: 640 vectors changing on deploy. Adds a paid-or-sleeping database (Neon free tier suspends after 5 minutes idle, adding wake-up latency), connection handling and migrations. The pgvector skills are already covered by the Berlin Pulse project. |
| **Dense only** | 55% / 44% / 50%: weak on code names (`np.kron`, `rk4`) and short questions. |
| **BM25 only** | Fails on everyday wording (28% on real learners). |
| **Embeddings API** (Voyage, Gemini) | Would likely embed better, but sends every learner question to one more company (privacy page, DPA) and adds a network call. Revisit if a stronger local model doesn't close the gap. |
| **Whole current lesson in context, no retrieval** | Not measured yet; planned as a baseline in Milestone 2 (on-page questions only; cannot answer off-page ones). |

## Consequences

- **Good:** no database to run, pay for or wake; index is versioned with the content; retrieval is fast and deterministic; eval harness and API share one Python module.
- **Must do:** rebuild `chunks.json` and embeddings whenever a lesson ships (the loader refuses mismatched files). Run `npm run build` first so the anchor check sees current HTML.
- **Accepted limits (tracked in `ai-tutor-planning/follow-ups.md`):** the model reads 512 tokens per chunk (#9); "is this answerable?" cannot be decided by similarity (#8, moves to the LLM in Milestone 2); the evaluation sets are small and partly model-written (#1-#5).

## Revisit when

- The corpus passes ~10,000 chunks, or content must change without a deploy, or learner data needs storing: reconsider a database.
- Milestone 2 shows the model answers badly despite the right chunks: try a reranker or a stronger embedding model before changing storage.
