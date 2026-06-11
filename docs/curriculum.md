# Curriculum & Research Framing

Slow-changing reference for the Pixels2GenAI curriculum structure and the
thesis research context. Split out of CLAUDE.md so the project guide stays a
rule-book. The machine-readable source of truth is
[`src/data/curriculum/modules.ts`](../src/data/curriculum/modules.ts) and
[`src/data/curriculum/subtopics.ts`](../src/data/curriculum/subtopics.ts).

## Module Framework Mapping

The curriculum is 15 modules + a capstone (193 leaf exercises), organised
across three DBR cycles:

| Module | Topic | Framework | Theory/Practice | Cycle (Stage) |
|--------|-------|-----------|-----------------|----------------|
| 0  | Foundations & Definitions       | F2 (Conceptual)   | 50/50 | I — Foundations |
| 1  | Pixel Fundamentals              | F1 (Hands-On)     | 25/75 | I |
| 2  | Geometry & Mathematics          | F1 (Hands-On)     | 25/75 | I |
| 3  | Transformations & Effects       | F1 (Hands-On)     | 25/75 | I |
| 4  | Fractals & Recursion            | F1+F2 Hybrid      | 35/65 | I |
| 5  | Simulation & Emergent Behaviour | F1 (Hands-On)     | 25/75 | I |
| 6  | Noise & Procedural Generation   | F1 (Hands-On)     | 25/75 | II — Machine Learning |
| 7  | Classical Machine Learning      | F2 (Deep-Dive)    | 50/50 | II |
| 8  | Animation & Time                | F1 (Hands-On)     | 25/75 | II |
| 9  | Neural Networks                 | F2 (Deep-Dive)    | 50/50 | II |
| 10 | TouchDesigner Fundamentals      | F2 (Deep-Dive)    | 50/50 | II |
| 11 | Interactive Systems             | F1 (Hands-On)     | 25/75 | II |
| 12 | Generative AI Models            | F2 (Deep-Dive)    | 50/50 | III — Generative AI |
| 13 | AI + TouchDesigner Integration  | F2 (Deep-Dive)    | 50/50 | III |
| 14 | Data as Material                | F1 (Hands-On)     | 25/75 | III |
| 15 | Capstone Project                | F3 (Project)      | 20/80 | III |

**Framework types**:
- **F1 (Hands-On)**: Overview → Quick Start → Core Concepts → Exercises (Execute/Modify/Create) → Summary
- **F2 (Conceptual)**: Big Question → Part 1-3 → Synthesis Project
- **F3 (Project)**: Overview → Phase 1-4 → Community Showcase

## Research Context (Thesis)

The project follows **Design-Based Research (DBR)** methodology with 5
research questions. The full RQ list lives in
[`src/data/site/research.ts`](../src/data/site/research.ts):

- **RQ1 — Framework Design**: pedagogical principles scaffolding arrays → generative AI
- **RQ2 — Cognitive Load**: decomposing complex concepts under cognitive-load constraints
- **RQ3 — Integration Pathways**: real-time systems (TouchDesigner) ⨯ progressive AI learning
- **RQ4 — Assessment**: technical proficiency, creative expression, conceptual understanding
- **RQ5 — Transfer**: how learners transfer foundational concepts to novel creative AI contexts

### DBR Cycles
- **Cycle I — Foundations**: Modules 00-05
- **Cycle II — Machine Learning**: Modules 06-11
- **Cycle III — Generative AI**: Modules 12-15

Cycle data is in `src/data/site/research.ts` (`CYCLES`). The exhibition
(March 2026, Berlin) and workshop (Feb 2026, Berlin) data — populated as past
events — is in `src/data/site/exhibitions.ts` and `src/data/site/workshops.ts`.
