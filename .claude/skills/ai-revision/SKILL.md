---
name: ai-revision
description: Detect and revise AI-generated language patterns in documentation to ensure authentic, human-quality writing. Use when reviewing lesson MDX files (or any v1 RST), checking for AI patterns, humanizing documentation, or preparing content for thesis submission. Activate when user says "check for AI patterns", "revise text", "humanize", "ai audit", or "check documentation quality".
---

# AI Revision Skill

## Skill Overview
This skill analyzes documentation for AI-generated language patterns and provides targeted transformations to produce authentic, human-quality academic writing. It implements the full AI Content Revision Framework documented in `thesis_automation/references/ai-revision-framework.md`.

## When to Use This Skill
- After generating or hand-porting a lesson MDX file
- After writing a v1 README.rst (when working in the legacy `numpy-to-genAI` repo)
- Before marking a module / lesson complete
- When preparing content for thesis submission
- When reviewing documentation quality

The patterns and transformations are format-agnostic — they apply identically to MDX prose and RST prose. Only embedding syntax (`<Figure>` vs `.. figure::`, `<Dropdown>` vs `.. dropdown::`) differs.

---

## Analysis Workflow

### Step 1: Read the Target Document
Read the target file (`src/content/lessons/<slug>.mdx` for v2, or `content/Module_NN_*/.../README.rst` for v1). Note total word count and section structure.

### Step 2: Sentence-Level Pattern Detection

Scan each sentence for these patterns:

| ID | Pattern | What to Look For | Example |
|----|---------|-------------------|---------|
| S-01 | Uniform sentence length | Sentences clustering around 18-22 words | All sentences roughly the same length |
| S-02 | SVO uniformity | Consistent Subject-Verb-Object without variation | "The kernel processes the image. The function returns the result." |
| S-03 | Generic topic sentences | Openings that could apply to any tutorial | "This fundamental concept is essential for understanding..." |
| S-04 | Parenthetical synonyms | Explaining terms with synonyms in parentheses | "blur kernel (smoothing)", "edge detection (finding boundaries)" |
| S-05 | Three-item lists | Lists of exactly three items | "...essential for X, Y, and Z" |
| S-06 | Filler phrases | Phrases adding no information | "It is important to note that", "It should be mentioned that" |
| S-07 | Hedging absence | Declarative statements without qualification | "X causes Y" instead of "X typically causes Y" |

### Step 3: Paragraph-Level Pattern Detection

| ID | Pattern | What to Look For | Example |
|----|---------|-------------------|---------|
| P-01 | Definition-first structure | Paragraphs starting with dictionary-style definitions | "A fractal is a geometric shape that..." |
| P-02 | Uniform paragraph length | All paragraphs approximately same length | 4-5 sentences each, consistently |
| P-03 | Predictable transitions | Overuse of "Additionally," "Furthermore," "Moreover" | Every paragraph starts with these |
| P-04 | Linear information flow | Strictly sequential with no callbacks to earlier concepts | No references back |
| P-05 | Missing topic sentences | Paragraphs lacking clear focus statement | Rambling explanations |

### Step 4: Section-Level Pattern Detection

| ID | Pattern | What to Look For | Example |
|----|---------|-------------------|---------|
| X-01 | Template adherence | Rigid adherence to standard educational templates | Every module identical structure |
| X-02 | Generic hooks | Opening hooks appearing in every tutorial | "From Instagram filters to neural networks..." |
| X-03 | Trivia box format | "Did You Know?" or "Fun Fact" boxes | Information as trivia |
| X-04 | Parallel bullet lists | Summary bullets with identical grammatical structure | All start with same part of speech |
| X-05 | Boilerplate conclusions | Generic concluding statements | "This foundational knowledge prepares you for..." |

### Step 5: Content-Level Pattern Detection

| ID | Pattern | What to Look For | Example |
|----|---------|-------------------|---------|
| C-01 | Standard examples | Examples appearing in every tutorial on the topic | Ferns, coastlines, lightning for fractals |
| C-02 | Wikipedia-style definitions | Definitions matching Wikipedia phrasing | Verbatim or near-verbatim matches |
| C-03 | Shallow historical references | Name-dropping without substantive discussion | "Rosenblatt introduced the perceptron in 1958" (and nothing more) |
| C-04 | Buzzword usage | Trendy terms without precise meaning | "paradigm shift", "revolutionary", "cutting-edge" |
| C-05 | Missing nuance | Oversimplified claims without caveats | "CNNs are inspired by the visual cortex" |

### Step 6: Code Comment Pattern Detection

| ID | Pattern | What to Look For | Example |
|----|---------|-------------------|---------|
| CD-01 | Redundant comments | Comments repeating what the code says | `x = 5  # Set x to 5` |
| CD-02 | Missing "why" comments | Comments explain "what" but not "why" | No rationale for design choices |
| CD-03 | Generic descriptions | Comments applicable to any code | `# Process the data` |
| CD-04 | Uniform comment style | All comments same length and structure | Every comment one short sentence |

---

## Risk Level Classification

### Risk Definitions

| Risk Level | Definition | Detection Likelihood | Priority |
|------------|------------|---------------------|----------|
| **CRITICAL** | Multiple AI patterns in single sentence/paragraph; generic content likely in AI training data | >80% | Immediate -- complete rewrite |
| **HIGH** | Clear AI patterns; formulaic structure; likely flagged by detection tools | 60-80% | Substantial transformation needed |
| **MEDIUM** | Some AI-like characteristics; technically accurate but generic | 30-60% | Targeted revisions |
| **LOW** | Minor AI patterns; mostly authentic or technical content | 10-30% | Light editing |
| **MINIMAL** | Code blocks, math formulas, specific technical details | <10% | Verify accuracy only |

### Risk Multipliers

| Combination | Multiplier |
|-------------|------------|
| Multiple S-patterns in one paragraph | 1.5x |
| X-pattern + P-pattern in same section | 1.5x |
| C-01 (standard examples) + P-01 (definition-first) | 2x |
| Generic hook + boilerplate conclusion | 2x |
| Three or more trivia boxes in one module | 1.5x |

---

## Transformation Techniques

### Sentence-Level Transforms

**T-S01: Sentence Length Variation**
- Vary between short (5-10 words), medium (15-20), and long (25-35)
- Break monotony with a punchy short sentence after a long one

**T-S02: Structure Inversion**
- Use passive voice selectively for variety
- Front adverbials: "Unlike traditional approaches, this method..."
- Cleft sentences: "What makes this technique powerful is..."

**T-S03: Specificity Injection**
- Lead with specific numbers, concrete examples, or unusual angles
- Before: "Convolution is widely used in image processing."
- After: "A single 3x3 convolution kernel can detect edges, blur noise, or sharpen details -- all by changing nine numbers."

**T-S04: Parenthetical Elimination**
- Remove or integrate synonyms naturally into prose
- Before: "The kernel (filter mask) slides across..."
- After: "The kernel slides across... This small matrix, sometimes called a filter mask, determines..."

**T-S05: List Restructuring**
- Use two items, four items, or convert to prose
- Avoid the AI-typical three-item pattern

**T-S06: Filler Removal**
- Delete entirely: "It is important to note that", "It should be mentioned that", "It is worth noting that"
- Just state the point directly

**T-S07: Qualification Addition**
- Add hedging where appropriate: "typically", "in most cases", "under certain conditions"
- Avoid making universal claims without qualification

### Paragraph-Level Transforms

**T-P01: Definition Deferral**
- Lead with application, consequence, or question -- defer the formal definition
- Before: "A fractal is a geometric shape that exhibits self-similarity."
- After: "Zoom into a coastline on Google Maps. Keep zooming. The jagged pattern never smooths out -- you see the same complexity at every scale. Mathematicians call this property self-similarity, and shapes exhibiting it are called fractals."

**T-P02: Transition Diversification**
- Replace "Additionally/Furthermore/Moreover" with varied connectives
- Use implicit transitions (logical flow without explicit markers)
- Try contrastive: "while", "whereas", "on the other hand"

**T-P03: Rhetorical Questions**
- Insert questions to engage: "But what happens when the kernel reaches the image border?"

**T-P04: Contrastive Structures**
- Use "while," "whereas," "although," "unlike" for nuanced comparisons

### Section-Level Transforms

**T-X01: Hook Replacement**
- Replace generic hooks with specific, unusual, or field-relevant angles
- Before: "From Instagram filters to neural networks, convolution is everywhere."
- After: "In 1985, a Pixar engineer needed to blur a reflection in a teapot. The solution -- sliding a weighted grid across pixel values -- turned out to be the same operation neuroscientists had observed in cat visual cortex decades earlier."

**T-X02: Trivia Box Conversion**
- Convert "Did You Know?" to "Technical Note:", "Historical Context:", or integrate into prose
- In v2 MDX, prefer `<Admonition type="dyk" title="Technical note · …">` with a *specific* heading over a generic "Did You Know?"
- Trivia format signals AI-generated content

**T-X03: Summary Transformation**
- Mix prose with embedded lists
- Vary grammatical structures in bullet points
- Add forward-looking connections

### Content-Level Transforms

**T-C01: Example Substitution**
- Replace standard examples with unusual, specific, or field-relevant ones
- Fractals: Instead of ferns/coastlines, use Kimetsu no Yaiba patterns, GPU heat dissipation grids
- Neural networks: Instead of MNIST, use artistic style classification

**T-C02: Historical Depth**
- Add historiographical nuance, contested interpretations, or consequences
- Before: "Rosenblatt introduced the perceptron in 1958."
- After: "Rosenblatt's 1958 perceptron sparked fierce debate -- Minsky and Papert's 1969 critique nearly killed neural network research for a decade, redirecting funding toward symbolic AI until backpropagation revived the field in the 1980s."

**T-C03: Nuance Addition**
- Add caveats, edge cases, or contested aspects
- "CNNs are loosely inspired by visual cortex" (add "loosely")

### Code Comment Transforms

**T-CD01: Why-Comments**
- Add rationale: `# Use uint8 because PIL expects 0-255 range for RGB`

**T-CD02: Edge Case Documentation**
- Note specific behaviors: `# np.clip needed here -- values can exceed 255 after blending`

---

## Citation Analysis

Check citations against these categories:

| Category | Description | Action |
|----------|-------------|--------|
| **Substantive** | Supports specific claim with discussion | Keep -- no change needed |
| **Bracket-only** | Appears as `[Author2020]_` (v1) or `[1]` (v2) without integration | Integrate into prose |
| **Name-drop** | Author mentioned but contribution not explained | Add substance or remove |
| **Missing** | Claim requires citation but lacks one | Add citation or qualify with hedging |

**Integration example**:
- Bracket-only: "Convolution is fundamental to image processing [Gonzalez2018]_."
- Integrated: "Gonzalez and Woods (2018) categorize convolution-based operations by kernel symmetry, showing that separable kernels reduce computation from O(n^2) to O(2n) [Gonzalez2018]_."

---

## Preservation List (Do NOT Transform)

Some content should be preserved unchanged regardless of AI pattern detection:
- Specific numerical examples from implementations
- Unusual references (e.g., anime for fractals, game engines for rendering)
- Hardware-specific observations (CUDA performance, GPU memory)
- Error messages and debugging notes
- Version-specific behaviors
- Mathematical formulas and algorithm pseudocode
- Code blocks (verify accuracy, but do not restyle for "authenticity")

---

## Output Report Format

After analysis, produce a report structured as:

```markdown
# AI Revision Report: [Lesson slug or Module ID]

**Document**: [path to MDX or RST file]
**Word Count**: [X words]
**Overall Risk Level**: [CRITICAL / HIGH / MEDIUM / LOW / MINIMAL]

## Pattern Summary
| Pattern Category | Count | Highest Risk |
|-----------------|-------|--------------|
| Sentence-level (S-*) | X | [level] |
| Paragraph-level (P-*) | X | [level] |
| Section-level (X-*) | X | [level] |
| Content-level (C-*) | X | [level] |
| Code comments (CD-*) | X | [level] |

## Priority Actions (ranked by risk)

### 1. [CRITICAL/HIGH] [Pattern ID]: [Description]
**Location**: [Section / line reference]
**Current text**: "[quoted text]"
**Issue**: [Pattern detected]
**Recommended transformation**: [T-XX technique]
**Suggested revision**: "[revised text]"

### 2. ...

## Citation Analysis
- Substantive: X
- Bracket-only: X (list them)
- Name-drop: X (list them)
- Missing: X (list claims needing citations)

## Preservation Notes
[Content identified as safe to preserve unchanged]
```

---

**After revision, re-read the document to verify transformations sound natural and maintain academic accuracy. Revisions should improve authenticity without sacrificing clarity or correctness.**
