# AI Content Revision Framework
## Reference Document for Academic Module Analysis

**Source**: Consolidated from `thesis_notes/module-verifications/ai_revision_framework.md`
**Purpose**: Complete set of AI detection patterns, transformation techniques, and academic writing guidelines for revising educational content.

---

## Part 1: AI Detection Patterns

### 1.1 Sentence-Level Patterns

| Pattern ID | Pattern Name | Description | Example |
|------------|--------------|-------------|---------|
| S-01 | Uniform sentence length | AI clusters around 18-22 words per sentence | "The convolution operation slides a kernel across the image computing weighted sums at each position to produce output values." (19 words) |
| S-02 | Subject-verb-object uniformity | Consistent SVO structure without variation | "The kernel processes the image. The function returns the result. The algorithm computes the output." |
| S-03 | Generic topic sentences | Opening sentences that could apply to any tutorial | "This fundamental concept is essential for understanding..." |
| S-04 | Parenthetical synonyms | Explaining terms with synonyms in parentheses | "blur kernel (smoothing)", "edge detection (finding boundaries)" |
| S-05 | Three-item lists | Lists of exactly three items | "...essential for X, Y, and Z" |
| S-06 | Filler phrases | Phrases that add no information | "It is important to note that", "It should be mentioned that" |
| S-07 | Hedging absence | Declarative statements without qualification | "X causes Y" instead of "X typically causes Y" |

### 1.2 Paragraph-Level Patterns

| Pattern ID | Pattern Name | Description | Example |
|------------|--------------|-------------|---------|
| P-01 | Definition-first structure | Paragraphs starting with dictionary-style definitions | "A fractal is a geometric shape that exhibits self-similarity at different scales." |
| P-02 | Uniform paragraph length | All paragraphs approximately same length | 4-5 sentences each, consistently |
| P-03 | Predictable transitions | Overuse of "Additionally," "Furthermore," "Moreover" | Every paragraph starts with these |
| P-04 | Linear information flow | Strictly sequential presentation without callbacks | No references to earlier concepts |
| P-05 | Missing topic sentences | Paragraphs that lack clear focus statement | Rambling explanations |

### 1.3 Section-Level Patterns

| Pattern ID | Pattern Name | Description | Example |
|------------|--------------|-------------|---------|
| X-01 | Template adherence | Rigid adherence to standard educational templates | Every module: Overview -> Concepts -> Exercises -> Summary |
| X-02 | Generic hooks | Opening hooks that appear in every tutorial | "From Instagram filters to neural networks..." |
| X-03 | Trivia box format | "Did You Know?" or "Fun Fact" boxes | Information delivery as trivia |
| X-04 | Parallel bullet lists | Summary bullets with identical grammatical structure | All bullets start with verbs or all start with nouns |
| X-05 | Boilerplate conclusions | Generic concluding statements | "This foundational knowledge prepares you for..." |

### 1.4 Content-Level Patterns

| Pattern ID | Pattern Name | Description | Example |
|------------|--------------|-------------|---------|
| C-01 | Standard examples | Examples appearing in every tutorial on the topic | Ferns, coastlines, lightning for fractals |
| C-02 | Wikipedia-style definitions | Definitions matching Wikipedia phrasing | Verbatim or near-verbatim matches |
| C-03 | Shallow historical references | Name-dropping without substantive discussion | "Rosenblatt introduced the perceptron in 1958" |
| C-04 | Buzzword usage | Trendy terms without precise meaning | "paradigm shift", "revolutionary", "cutting-edge" |
| C-05 | Missing nuance | Oversimplified claims without caveats | "CNNs are inspired by the visual cortex" |

### 1.5 Code Comment Patterns

| Pattern ID | Pattern Name | Description | Example |
|------------|--------------|-------------|---------|
| CD-01 | Redundant comments | Comments that repeat what code says | `x = 5  # Set x to 5` |
| CD-02 | Missing "why" comments | Comments explain "what" but not "why" | No explanation of design choices |
| CD-03 | Generic descriptions | Comments that could apply to any code | `# Process the data` |
| CD-04 | Uniform comment style | All comments same length and structure | Every comment is one short sentence |

---

## Part 2: Risk Level Classification

### 2.1 Risk Level Definitions

| Risk Level | Definition | Detection Likelihood | Revision Priority |
|------------|------------|---------------------|-------------------|
| **CRITICAL** | Multiple AI patterns in single sentence/paragraph; generic content that appears verbatim in AI training data | Very High (>80%) | Immediate - Complete rewrite required |
| **HIGH** | Clear AI patterns; formulaic structure; could be flagged by detection tools | High (60-80%) | High - Substantial transformation needed |
| **MEDIUM** | Some AI-like characteristics; technically accurate but generic | Moderate (30-60%) | Medium - Targeted revisions recommended |
| **LOW** | Minor AI patterns; mostly authentic or technical content | Low (10-30%) | Low - Light editing sufficient |
| **MINIMAL** | Code blocks, mathematical formulas, specific technical details | Very Low (<10%) | Optional - Verify accuracy only |

### 2.2 Risk Multipliers

| Combination | Risk Multiplier |
|-------------|-----------------|
| Multiple S-patterns in one paragraph | 1.5x |
| X-pattern + P-pattern in same section | 1.5x |
| C-01 (standard examples) + P-01 (definition-first) | 2x |
| Generic hook + boilerplate conclusion | 2x |
| Three or more trivia boxes in one module | 1.5x |

---

## Part 3: Transformation Techniques

### 3.1 Sentence-Level Transformations

**T-S01: Sentence Length Variation** - Vary between short (5-10), medium (15-20), and long (25-35) sentences.

**T-S02: Structure Inversion** - Use passive voice selectively, fronted adverbials, cleft sentences.

**T-S03: Specificity Injection** - Lead with specific numbers, concrete examples, or unusual angles.

**T-S04: Parenthetical Elimination** - Remove or integrate synonyms naturally.

**T-S05: List Restructuring** - Use two items, four items, or convert to prose.

**T-S06: Filler Removal** - Delete empty phrases entirely.

**T-S07: Qualification Addition** - Add appropriate academic hedging.

### 3.2 Paragraph-Level Transformations

**T-P01: Definition Deferral** - Lead with application, consequence, or question; defer definition.

**T-P02: Transition Diversification** - Replace "Additionally/Furthermore/Moreover" with varied connectives or implicit transitions.

**T-P03: Rhetorical Questions** - Insert questions to engage reader.

**T-P04: Contrastive Structures** - Use "while," "whereas," "although," "unlike."

### 3.3 Section-Level Transformations

**T-X01: Hook Replacement** - Use specific, unusual, or field-specific angles instead of generic hooks.

**T-X02: Trivia Box Conversion** - Convert "Did You Know?" to "Technical Note:", "Historical Context:", or integrate into prose.

**T-X03: Summary Transformation** - Mixed prose with embedded lists, varied grammatical structures.

### 3.4 Content-Level Transformations

**T-C01: Example Substitution** - Replace standard examples with unusual, specific, or field-relevant ones.

**T-C02: Historical Depth** - Add historiographical nuance, contested interpretations, or consequences.

**T-C03: Nuance Addition** - Add caveats, edge cases, or contested aspects.

### 3.5 Code Comment Transformations

**T-CD01: Why-Comments** - Add rationale for design choices.

**T-CD02: Edge Case Documentation** - Document specific edge cases, version behaviors, or gotchas.

---

## Part 4: Citation Analysis

### 4.1 Citation Categories

| Category | Description | Revision Need |
|----------|-------------|---------------|
| **Substantive** | Citation supports specific claim with discussion | Low -- keep as is |
| **Bracket-only** | Citation appears as [Author2020] without integration | Medium -- integrate into prose |
| **Name-drop** | Author mentioned but contribution not explained | High -- add substance or remove |
| **Missing** | Claim that requires citation but lacks one | Critical -- add citation or qualify |

### 4.2 Citation Integration

```
BRACKET-ONLY: "Convolution is fundamental to image processing [Gonzalez2018]."
INTEGRATED: "Gonzalez and Woods (2018) categorize convolution-based operations by kernel properties..."
```

---

## Part 5: Output Report Structure

See `thesis_automation/phases/03_validate_ai.md` (in v1) for the analysis prompt that uses this framework to generate structured reports. The `.claude/skills/ai-revision/` skill in v2 implements the same output format.

---

## Part 6: Special Considerations

### Technical Content Handling
Mathematical formulas, algorithm descriptions, and precise technical specifications are low detection risk but high accuracy risk. Verify accuracy; do not transform for style.

### Cited Claims
Content directly attributed to sources is low detection risk. Verify citation accuracy; consider integrating bracket-only citations.

### Code Blocks
Functional code is minimal detection risk but high accuracy risk. Verify code runs correctly; enhance comments per T-CD techniques.

### Preservation List
Some content should be preserved unchanged:
- Specific numerical examples from implementations
- Unusual references (e.g., Kimetsu no Yaiba for fractals)
- Hardware-specific observations
- Error messages and debugging notes
- Version-specific behaviors

---

*Framework Version 1.0 — ported from v1 (numpy-to-genAI). Format-agnostic: applies to both v1 RST and v2 MDX content.*
