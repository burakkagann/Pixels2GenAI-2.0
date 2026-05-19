# Exercise Scaffolding Rules
## Execute -> Modify -> Create Framework

**Source**: Consolidated from `thesis_notes/exercise-structure-validation-promt.md`

---

## Context

**Target audience**: Semi-beginners to semi-experienced programmers. They are NOT expected to translate mathematics or theory into code from scratch. They ARE expected to run scripts, change labeled parameters, and fill in short TODOs in heavily scaffolded starter code.

**Educational philosophy**: Theory (40%) / Practice (60%). Visual-first pedagogy with immediate feedback loops. Every exercise must produce a visible output that reinforces the concepts taught in the Core Concepts section.

**NumPy functions**: When a new NumPy function is introduced in any exercise, provide brief information on what it is and what it does, so learners also learn about NumPy functions and their purpose and use case.

---

## The Three Scaffolding Levels

### Exercise 1 -- Execute (Run and Observe)
The learner runs a complete, working script and observes the output. No code changes required.

**Pass criteria**:
- [ ] Script runs without errors and produces a visible output (image, GIF, or terminal display)
- [ ] Output directly demonstrates at least one Core Concept from the module
- [ ] Lesson includes reflection questions that connect the output back to theory
- [ ] Reflection questions have collapsible answer dropdowns (`<Dropdown>` in v2 MDX, `.. dropdown::` in v1 RST) so learners can self-check

**Red flags**:
- Script requires manual setup beyond `python script_name.py`
- Output is abstract or disconnected from what was taught
- No reflection prompts -- learner runs the script and moves on without thinking

### Exercise 2 -- Modify (Change Labeled Parameters)
The learner changes 2-5 clearly labeled values in the script, re-runs it, and observes how the output changes.

**Pass criteria**:
- [ ] Script has a clearly marked area where the learner makes changes -- either a `CONFIG` section at the top OR inline edit zones marked with `<-- CHANGE THIS`
- [ ] Each modifiable value has an inline comment explaining what it controls
- [ ] Lesson defines **explicit numbered Goals** (Goal 1, Goal 2, ...) -- each goal asks the learner to change specific values
- [ ] Each goal has a "What to expect" dropdown explaining the expected result
- [ ] Goals are ordered from simplest change to most interesting discovery
- [ ] Learner changes are limited to the marked area -- no editing of algorithm code
- [ ] Re-running the script after changes produces a visibly different output

**Red flags**:
- No marked edit area -- parameters are buried inside functions or classes
- Script runs automatically with no learner input (same as Exercise 1)
- Parameters are unlabeled or require understanding internal logic to choose values
- Changing parameters produces no visible difference in output
- More than 5 parameters exposed (cognitive overload)

### Exercise 3 -- Create (Fill TODOs in Starter Code)
The learner completes a partially-written script by filling in 3-6 TODOs. The script is 60-85% complete. The learner writes approximately 5-15 lines of code total.

**Pass criteria**:
- [ ] Starter code file exists with clearly marked `# TODO:` comments
- [ ] Each TODO has an inline comment explaining what to write and WHY
- [ ] Steps that require framework-specific knowledge (PyTorch, TensorFlow, library APIs) are PROVIDED, not left as TODOs
- [ ] TODOs involve conceptual operations the learner understands from Core Concepts (e.g., blending, thresholding, array creation) -- not library-specific boilerplate
- [ ] Script includes a CONFIG section or clearly modifiable variables so learners can experiment AFTER completing the TODOs
- [ ] Lesson provides progressive hints as collapsible dropdowns (Hint 1, Hint 2, ..., Complete Solution)
- [ ] Completing the TODOs produces a satisfying, visible output (the learner should feel they CREATED something)
- [ ] A "Make It Your Own" section encourages experimentation after TODOs are done
- [ ] New concepts required for the TODOs (if any) are explained in a collapsible dropdown BEFORE the starter code

**Red flags**:
- TODOs require writing framework-specific code the learner hasn't been taught
- TODOs require translating mathematical formulas into code (unless formula is given inline)
- Starter code is <50% complete -- learner is essentially writing from scratch
- Starter code is >90% complete -- learner is just uncommenting lines (no learning)
- No hints provided -- learner has no support if stuck
- Script runs for extended time (>5 minutes) with no intermediate feedback
- Output is not meaningfully different from Exercise 1 output (learner didn't CREATE anything new)
- No way to experiment after completing TODOs

---

## CONFIG vs Inline Edit Zones

### Use a CONFIG section when:
The parameters being modified are genuine domain configuration -- things a practitioner would naturally extract to the top of a script.

**Examples**: ML hyperparameters (`LEARNING_RATE`, `EPOCHS`), simulation parameters (`NUM_PARTICLES`, `TIMESTEP`), image processing settings (`BLUR_RADIUS`, `THRESHOLD`).

### Use inline edit zones when:
The lines being modified ARE the learning objective -- where abstracting values into variables would hide the concept being taught.

**Examples**: Array indexing operations, direct algorithm steps, mathematical expressions.

Mark inline edit zones clearly:
```python
# =============================================
# MODIFY the values below to achieve each goal
# =============================================
image[:, :, 0] = 255  # Red channel    <-- CHANGE THIS
image[:, :, 1] = 128  # Green channel  <-- CHANGE THIS
image[:, :, 2] = 0    # Blue channel   <-- CHANGE THIS
# =============================================
```

### Decision test:
> "Would a professional programmer naturally extract this value into a config variable?"
> - **Yes** -> Use a CONFIG section
> - **No, the code IS the lesson** -> Use inline edit zones

---

## Cross-Exercise Checks

- [ ] **Progressive difficulty**: Exercise 1 < Exercise 2 < Exercise 3 in required effort
- [ ] **Theory reinforcement**: Each exercise connects to at least one Core Concept
- [ ] **No passive exercises**: Every exercise requires the learner to DO something
- [ ] **Visual feedback**: Every exercise produces a visible output image or animation
- [ ] **Self-contained**: Each exercise works independently (no Exercise 2 output needed for Exercise 3)
- [ ] **Duration budget**: Exercise 1 (3-5 min) + Exercise 2 (8-12 min) + Exercise 3 (10-15 min) = 20-30 min total
- [ ] **Cognitive load**: No more than 3-4 new concepts introduced across ALL exercises combined

---

## Review Classification

Each exercise should be classified as:
- **PASS**: Meets all pass criteria, no red flags
- **NEEDS WORK**: Meets most criteria but has 1-2 fixable issues
- **BROKEN**: Fails the fundamental scaffolding level (e.g., "Modify" exercise with nothing to modify)

For NEEDS WORK and BROKEN exercises, propose 2-3 concrete alternatives ranked by implementation effort.
