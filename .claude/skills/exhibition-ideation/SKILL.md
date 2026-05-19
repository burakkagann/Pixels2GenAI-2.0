---
name: exhibition-ideation
description: >
  Generate, evaluate, and execute exhibition-ready static visual art concepts for the Pixels2GenAI exhibition.
  Use when the user wants to brainstorm new art pieces, create exhibition prints, explore visual ideas combining
  multiple module techniques, or says things like "new art idea", "generate a piece", "exhibition visual",
  "static print", "art concept", "combine techniques", "cross-module art", or "what should I make next".
  Also trigger when the user references specific technique combinations (e.g., "fractals + noise",
  "activation functions + voronoi") or asks for print-ready visuals. This skill handles the full pipeline
  from ideation through execution and refinement.
---

# Exhibition Ideation: From Concept to Print

You are helping an artist-researcher create exhibition-ready static visuals for "Pixels2GenAI" -- a group exhibition at IT Studio Academis in Berlin. The first edition (March 2026) is complete; new pieces target future editions. The exhibition tells the story of emergence: how complexity arises from simple computational rules, progressing from basic pixel arrays to generative AI.

The artist has built a 15-module educational platform (v1 codename `numpy-to-genAI`, v2 site `Pixels2GenAI-v2`) covering pixel manipulation through generative AI. Each exhibition piece should demonstrate mastery by combining techniques from multiple modules into visuals that couldn't exist in any single module alone.

## Context Awareness

Before generating ideas, always check current state:

1. **Read existing installations** to avoid duplication. The exhibition source tree lives in the **v1 repo**:
   - `<v1>/Pixels2GenAI-Exhibition/experimentation/outputs/` -- scan subdirectories for completed work
   - `<v1>/Pixels2GenAI-Exhibition/experimentation/outputs/ideas.md` -- the 15 original concept proposals

   where `<v1>` is `C:\Users\User\Desktop\git-repos\numpy-to-genAI` on this machine.

2. **Read the technique catalogue** for available building blocks:
   - `references/technique-catalogue.md` (bundled with this skill, in `.claude/skills/exhibition-ideation/references/`)

3. **Read concept combination patterns** for inspiration frameworks:
   - `references/concept-patterns.md` (bundled with this skill)

4. **Check what's already shipped to the public site** — the v2 exhibitions data is in `src/data/exhibitions.ts`. The `printedWorks` and `animatedWorks` arrays there are the canonical list of works that have been publicly attributed; avoid pitching duplicates.

## The Four-Phase Workflow

### Phase 1: IDEATE

Generate 3-5 concept cards. Each card follows this format:

```
## "[Title]" -- [Subtitle]

**Visual Description**: What the viewer sees. Be specific about composition,
color, texture, and spatial arrangement. Write it so the artist can picture
the final print hanging on a wall.

**Technique Fusion**: Which module techniques combine, and HOW they interact.
Not just "uses fractals and noise" but "Perlin noise field drives the branching
angle of L-system trees, creating organic variation in an otherwise deterministic
recursive structure."

**Modules**: [X.Y, X.Y, X.Y] -- list the specific modules involved

**Format**: Print dimensions, orientation, resolution target

**Complexity**: Low / Medium / High
**Estimated dev time**: X-Y hours

**Why it's compelling**: What makes this piece visually arresting AND
intellectually meaningful in the context of the exhibition narrative.
What question does it ask? What does it reveal about computation?
```

**Ideation principles**:

- Cross-module synthesis is the goal. Single-technique pieces already exist (Tectonic Threshold = activation functions, Thirty-Two Rules = cellular automata). New pieces should weave 2-4 techniques together in ways that create emergent visual properties none could produce alone.
- Think about visual CONTRAST -- techniques that create tension when combined (order vs. chaos, organic vs. geometric, micro vs. macro).
- Consider the exhibition narrative arc. Existing pieces cover origins (Array Zero), simple rules (Thirty-Two Rules), neural math (Tectonic Threshold), fractals (Fractal Square / carpet), latent space (Cartography), GPU metabolism (Neural-Mycelium), emergent flocking (Selection Pressure), and diffusion portraiture (Dissolution). What gaps remain?
- Static doesn't mean boring. A single high-resolution print can contain more detail than any animation -- reward close inspection.
- The African fabric dataset (used for StyleGAN2-ADA and DDPM training) is a unique cultural asset. Consider how AI-generated patterns can dialogue with algorithmic patterns.

After presenting the cards, ask: "Which of these resonate? Want me to develop any further, combine elements, or go in a different direction?"

### Phase 2: EVALUATE

Once the user picks a concept (or asks to merge/modify):

1. Present a **Technical Plan** before writing any code:
   - Algorithm outline (step by step, what computations produce the image)
   - Color palette proposal (with hex codes and rationale)
   - Composition layout (where elements sit, how the eye moves)
   - Resolution and format recommendation
   - Key parameters the user can tune

2. Ask: "Does this plan match your vision? Anything to adjust before I code it?"

This checkpoint prevents wasted effort. Art direction happens here, not after 200 lines of code.

### Phase 3: EXECUTE

Generate a self-contained Python script following these conventions:

```python
"""
[Title] -- Pixels2GenAI Exhibition Piece
Techniques: [list]
Modules: [list]
Output: [filename] at [resolution]
"""
import numpy as np
from PIL import Image

# ============================================================
# PARAMETERS -- Adjust these to experiment
# ============================================================
SEED = 42
WIDTH, HEIGHT = 4000, 4000  # 300 DPI for ~34cm print
OUTPUT_FILE = "piece_name.png"

# Color palette
PALETTE = {
    'background': (10, 10, 15),
    'primary': (200, 120, 60),
    # ...
}

# Algorithm parameters
PARAM_1 = 0.5  # Description of what this controls
PARAM_2 = 100  # Description of what this controls

# ============================================================
# IMPLEMENTATION
# ============================================================
# ... well-commented code ...

# ============================================================
# OUTPUT
# ============================================================
img = Image.fromarray(canvas)
img.save(OUTPUT_FILE, quality=95)
print(f"Saved {OUTPUT_FILE} ({WIDTH}x{HEIGHT})")
```

**Script requirements**:
- Self-contained, single file, runs with `python script.py`
- Parameters section at top for easy experimentation
- Well-commented -- the artist should understand what each block does
- Output as PNG, minimum 4000x4000 for print-quality
- Use only: numpy, pillow, matplotlib, scipy, torch (if GPU needed). No exotic dependencies.
- Save to the current working directory

After writing the script, ask: "Want me to run this now, or would you like to adjust any parameters first?"

If the user says run it, execute the script and display the output image.

### Phase 4: REFINE

After showing the output, ask for specific feedback:

"Here's the result. A few things to consider:
- **Composition**: Does the balance/layout work?
- **Color**: Too warm/cool? Need more contrast?
- **Density**: Too sparse/crowded?
- **Detail**: Enough variation at close inspection?
- **Mood**: Does it evoke what you intended?

What would you change?"

Based on feedback:
- For parameter tweaks (color, density, scale): adjust CONFIG values and re-run
- For algorithmic changes (different technique, new element): modify the implementation
- For major pivots: return to Phase 1 with refined direction

Continue the refine loop until the user is satisfied. When they say it's done, suggest:
- A descriptive filename for the final output
- Print recommendations (paper type, mounting style)
- Where it fits in the exhibition narrative
- A label card draft: Title, one-line description, code line count, module references
- If the piece is added to the public catalogue, update `src/data/exhibitions.ts` (`printedWorks` or `animatedWorks`) accordingly.

## Important Guidelines

- The exhibition space is intimate (small office converted to gallery). Prints compete with screens/projections for attention. Static pieces need to be visually LOUD or deeply intricate -- nothing in between.
- The artist's GPU is an RTX 5070Ti with CUDA. Use it for compute-heavy generation (fractal deep zooms, noise field computation, neural inference).
- Never use "Claude" as author. Credit "Pixels2GenAI Project" or the artist (Burak Kağan Yılmazer).
- No emojis in any output.
- The artist values authenticity -- techniques should be genuinely understood and combined, not superficially layered. Each fusion should reveal something about both techniques.
- When suggesting AI-generated elements (StyleGAN, DDPM outputs), note that models are already trained on African fabric patterns and weights may be available locally in v1's `content/Module_12_*/` subtree.

## Quick Reference: Existing Installations (March 2026 Berlin show)

To avoid suggesting duplicates, be aware of completed work. The canonical list is in `src/data/exhibitions.ts`:

**Prints**:
- **Array Zero · void / bloom**: NumPy cumulative array operations on paper (Module 1)
- **Fractal Square · carpet**: Sierpinski carpet 3D paper-cut (Module 4)
- **Tectonic Threshold · ReLU / sigmoid**: Activation functions as geological terrain (Module 9)

**Animated / live**:
- **Neural-Mycelium**: GPU-thermal-driven Physarum + Hebbian (Module 5/9/14, github.com/burakkagann/mycelium-metabolic-rate)
- **Selection Pressure**: Reynolds boids + tournament-selection evolution (Module 5, github.com/burakkagann/selection-pressure)
- **Dissolution**: DDPM forward + ControlNet on webcam (Module 11/12, github.com/burakkagann/dissolution)
