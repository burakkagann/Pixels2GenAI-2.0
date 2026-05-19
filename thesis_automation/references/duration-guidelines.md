# Duration Estimation Guidelines

**Source**: Extracted from CLAUDE.md Duration Estimation section
**Purpose**: Cognitive load management through strict time constraints

---

## Target Durations by Module Range

### Modules 0-6 (Foundation/Hands-On): 15-20 minutes maximum

| Section | Time |
|---------|------|
| Quick Start | 2-3 minutes (run code, see output) |
| Core Concepts | 5-8 minutes (read 2-4 concepts with examples) |
| Hands-On Exercises | 8-12 minutes (Execute -> Modify -> Create) |
| **Total** | **15-23 minutes (target: 18 min avg)** |

### Modules 7-15 (Advanced/Theory): 30-45 minutes maximum

| Section | Time |
|---------|------|
| Introduction | 3-5 minutes (Big Question + motivation) |
| Theory Sections | 12-18 minutes (Part 1, Part 2, Part 3) |
| Implementation | 10-15 minutes (code examples + explanation) |
| Exercises/Synthesis | 8-12 minutes (practice + challenge) |
| **Total** | **33-50 minutes (target: 40 min avg)** |

---

## Duration Estimation Formula

**Reading time** = (Word count / 200 words/min) x 1.5 multiplier
- 1.5 multiplier accounts for technical content being slower to read

**Code execution time** = Number of code blocks x 1 minute

**Exercise time**:
- Execute exercises: 3 minutes
- Modify exercises: 4 minutes
- Create exercises: 5 minutes
- Architect exercises: 8-10 minutes

---

## Cognitive Load Checkpoints

**Maximum cognitive load limits**:
- New concepts per exercise: 3-4 maximum (ideally 2-3)
- Code blocks per section: 5 maximum
- Exercises per module: 3 (Execute, Modify, Create)
- Figures/diagrams: 4-6 maximum
- References cited: 5-10 (don't overwhelm with citations)

**Red flags that duration is too long**:
- More than 4 new concepts introduced
- Core Concepts section exceeds 800 words
- More than 3 exercises in Hands-On section
- Exercise 3 (Create) requires more than 20 lines of new code
- Text-to-code ratio is >70% text (should be balanced)

---

## Content Trimming Guidelines

### For Modules 0-6 (exceeding 20 minutes):
1. Reduce Core Concepts from 4 -> 3 or 3 -> 2
2. Remove "Did You Know?" admonitions (keep only 1-2)
3. Shorten explanatory text
4. Combine similar exercises
5. Move advanced content to separate "Extension" exercise

### For Modules 7-15 (exceeding 45 minutes):
1. Split into multiple sub-exercises
2. Move deep-dives to `<Dropdown>` components (v2) or `.. dropdown::` (v1)
3. Provide "Quick Path" and "Deep Dive" alternatives
4. Reduce code examples (keep 1-2 most illustrative)
5. Move supplementary content to "Further Reading"

---

## Duration Declaration in Frontmatter

**v2 MDX** (`src/content/lessons/<slug>.mdx`):
```yaml
---
duration: "18–25 min"
level: "beginner"
load: "3 core concepts"
---
```

**v1 RST**:
```rst
:Duration: 18 minutes
:Level: Beginner
:Prerequisites: Module X.Y-1
```

For optional extensions:
```yaml
duration: "15 min (core) + 10 min (extensions)"
```

For theory-heavy modules:
```yaml
duration: "35 min (quick path) | 50 min (deep dive)"
```

---

## Total Course Time Budget: ~8 hours

- Modules 0-6 (7 modules x 18 min avg): ~126 min (2.1 hours)
- Modules 7-15 (9 modules x 40 min avg): ~360 min (6 hours)
- Total: ~486 min (8.1 hours)

Pacing options:
- **Intensive**: 2 days (4 hours/day)
- **Moderate**: 1 week (1.5 hours/day)
- **Relaxed**: 2 weeks (45 min/day)

---

*Extracted from CLAUDE.md. Duration targets are pedagogical, not format-specific — they apply identically to v1 RST and v2 MDX renderings.*
