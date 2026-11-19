/**
 * Node tests for the concept framework check (FW-5, src/lib/concepts/rules.mjs): a valid fixture passes, and every
 * rule in the build plan's section 4 has a fixture that fails it. Fixtures are built in memory from one valid
 * concept and one valid lesson, changed in one place each; file checks use a fake `exists`.
 * Run: npm run test:concepts      Author: Pixels2GenAI Project
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { conceptErrors, lessonErrors } from '../../src/lib/concepts/rules.mjs';

const ALL_FILES = () => true;

const question = () => ({
  q: 'A pixel is (90, 30, 0). What is its brightness?',
  options: [
    { text: '40', correct: true, why: '(90 + 30 + 0) / 3 = 40.' },
    { text: '120', why: 'That is the sum; brightness divides it by 3.' },
  ],
});

const recallQuestion = () => ({
  q: 'What is the brightness of the pixel (200, 40, 60)?',
  options: [
    { text: '100', correct: true, why: '(200 + 40 + 60) / 3 = 100.' },
    { text: '300', why: 'That is the sum; brightness divides it by 3.' },
  ],
});

const goodConcept = (id = 'brightness', extra = {}) => ({
  id,
  body: 'A digital photo is a grid of pixels, each with three numbers<Cite c="Gonzalez & Woods, 2018" />.',
  data: {
    id,
    title: 'A photo is a grid of brightness numbers',
    short: 'brightness numbers',
    keyIdea: 'Every pixel holds three numbers from 0 to 255; their average is its brightness.',
    introduced: { lesson: 'try' },
    figure: { kind: 'still', name: 'grid-zoom', folder: '/concepts/fig', phoneHeight: 1340,
      alt: 'A 6 by 6 patch of the photo, enlarged.', caption: 'A corner of the Dom, enlarged.' },
    worked: '(90 + 88 + 83) / 3 = 87',
    predict: question(),
    recall: recallQuestion(),
    cite: ['Gonzalez & Woods, 2018'],
    ...extra,
  },
});

const REFS = `<Hint kind="note" label="Sources (1)"><ol data-sources="">
<li>Gonzalez, R. C., & Woods, R. E. (2018). *Digital image processing* (4th ed.). Pearson.</li>
</ol></Hint>`;

const lessonSource = (screens, wrap = '<TryWrap minutes={2} recall={["a", "b", "c"]}>') => `
<MakeItFirst title="x" minutes={2}>
</MakeItFirst>
${screens}
${wrap}
${REFS}
</TryWrap>`;

const GOOD_SCREENS = `
<ConceptScreen id="a" n={1} of={3} minutes={1} />
<TryStep n={1} kind="predict" title="x" minutes={3} concept="a">
</TryStep>
<ConceptScreen id="b" n={2} of={3} minutes={1} />
<TryStep n={2} kind="write" title="x" minutes={2} concept="b">
</TryStep>
<ConceptScreen id="c" n={3} of={3} minutes={1} />
<TryStep n={3} kind="fix" title="x" minutes={3} concept="c">
</TryStep>`;

const library = (overrides = {}) => new Map(['a', 'b', 'c', 'd', 'e'].map((id) => [id, overrides[id] ?? goodConcept(id)]));
const lesson = (source, extra = {}) => ({ file: 'lesson.mdx', lesson: 'try', public: true, budget: 15, source, ...extra });

function failsWith(errors, pattern) {
  assert.ok(errors.some((error) => pattern.test(error)), `expected an error matching ${pattern}, got:\n${errors.join('\n') || '(none)'}`);
}

// ---------- valid fixtures pass ----------

test('a valid concept passes', () => {
  assert.deepEqual(conceptErrors(goodConcept(), ALL_FILES), []);
});

test('a valid lesson passes (15 min, alternating, recall in order)', () => {
  assert.deepEqual(lessonErrors(lesson(lessonSource(GOOD_SCREENS)), library()), []);
});

// ---------- each concept file rule ----------

test('fails: frontmatter id is not the file name (FW-2: one file per concept)', () => {
  const concept = goodConcept('a');
  concept.data.id = 'b';
  failsWith(conceptErrors(concept, ALL_FILES), /frontmatter id "b" is not the file name/);
});

test('fails: no keyIdea (CR-2)', () => {
  for (const keyIdea of [undefined, '', '   ']) {
    failsWith(conceptErrors(goodConcept('brightness', { keyIdea }), ALL_FILES), /no keyIdea/);
  }
});

test('fails: keyIdea over 20 words (CR-2)', () => {
  const keyIdea = 'Every single pixel in the photo holds three numbers for red, green and blue light, and their average is its brightness.';
  failsWith(conceptErrors(goodConcept('brightness', { keyIdea }), ALL_FILES), /keyIdea is \d+ words, over 20/);
});

test('passes: keyIdea of exactly 20 words (CR-2)', () => {
  const keyIdea = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty.';
  assert.ok(!conceptErrors(goodConcept('brightness', { keyIdea }), ALL_FILES).some((error) => /keyIdea/.test(error)));
});

test('fails: keyIdea of two sentences (CR-2)', () => {
  const keyIdea = 'A pixel holds three numbers. Their average is its brightness.';
  failsWith(conceptErrors(goodConcept('brightness', { keyIdea }), ALL_FILES), /keyIdea is more than one sentence/);
});

test('fails: no figure', () => {
  const concept = goodConcept();
  delete concept.data.figure;
  failsWith(conceptErrors(concept, ALL_FILES), /no figure/);
});

for (const missing of ['light.webp', 'dark.webp', 'light.phone.webp', 'dark.phone.webp']) {
  test(`fails: missing ${missing} figure file`, () => {
    const exists = (file) => !file.endsWith(`grid-zoom.${missing}`);
    failsWith(conceptErrors(goodConcept(), exists), new RegExp(`missing figure file .*grid-zoom\\.${missing.replace(/\./g, '\\.')}$`));
  });
}

test('fails: alt under 10 characters', () => {
  const concept = goodConcept();
  concept.data.figure.alt = 'a grid';
  failsWith(conceptErrors(concept, ALL_FILES), /alt missing or under 10/);
});

test('fails: no caption', () => {
  const concept = goodConcept();
  concept.data.figure.caption = '';
  failsWith(conceptErrors(concept, ALL_FILES), /no caption/);
});

test('fails: Explain over 70 words', () => {
  const concept = goodConcept();
  concept.body = Array.from({ length: 71 }, () => 'word').join(' ');
  failsWith(conceptErrors(concept, ALL_FILES), /Explain is 71 words/);
});

test('fails: no worked example', () => {
  const concept = goodConcept();
  concept.data.worked = '';
  failsWith(conceptErrors(concept, ALL_FILES), /no worked example/);
});

test('fails: prediction with 1 or 5 options', () => {
  for (const count of [1, 5]) {
    const concept = goodConcept();
    concept.data.predict.options = Array.from({ length: count }, (_, i) => ({ text: String(i), correct: i === 0, why: 'Because.' }));
    failsWith(conceptErrors(concept, ALL_FILES), /predict: needs 2-4 options/);
  }
});

test('fails: prediction with no or two correct options', () => {
  for (const flags of [[false, false], [true, true]]) {
    const concept = goodConcept();
    concept.data.predict.options.forEach((option, i) => { option.correct = flags[i]; });
    failsWith(conceptErrors(concept, ALL_FILES), /predict: needs exactly one correct option/);
  }
});

test('fails: a wrong option without feedback', () => {
  const concept = goodConcept();
  concept.data.predict.options[1].why = '';
  failsWith(conceptErrors(concept, ALL_FILES), /predict option 2 .*no feedback/);
});

test('fails: feedback over one sentence', () => {
  const concept = goodConcept();
  concept.data.predict.options[1].why = 'That is the sum. Divide it by 3.';
  failsWith(conceptErrors(concept, ALL_FILES), /more than one sentence/);
});

test('fails: feedback over 25 words', () => {
  const concept = goodConcept();
  concept.data.predict.options[1].why = `${Array.from({ length: 26 }, () => 'word').join(' ')}.`;
  failsWith(conceptErrors(concept, ALL_FILES), /feedback over 25 words/);
});

test('fails: recall feedback over one sentence, or over 25 words (R-3585-61)', () => {
  const two = goodConcept();
  two.data.recall.options[1].why = 'That is the sum. Divide it by 3.';
  failsWith(conceptErrors(two, ALL_FILES), /recall option 2 .*feedback is more than one sentence/);
  const long = goodConcept();
  long.data.recall.options[1].why = `${Array.from({ length: 26 }, () => 'word').join(' ')}.`;
  failsWith(conceptErrors(long, ALL_FILES), /recall option 2 .*feedback over 25 words/);
  const missing = goodConcept();
  missing.data.recall.options[1].why = '';
  failsWith(conceptErrors(missing, ALL_FILES), /recall option 2 .*no feedback/);
});

test('fails: no recall question, or a recall question breaking the same rules', () => {
  const none = goodConcept();
  delete none.data.recall;
  failsWith(conceptErrors(none, ALL_FILES), /recall: missing/);
  const bad = goodConcept();
  bad.data.recall.options[0].correct = false;
  failsWith(conceptErrors(bad, ALL_FILES), /recall: needs exactly one correct option/);
});

test('fails: no citation', () => {
  const concept = goodConcept();
  concept.data.cite = [];
  failsWith(conceptErrors(concept, ALL_FILES), /no citation/);
});

test("fails: a citation missing from the lesson's References", () => {
  const concepts = library({ b: goodConcept('b', { cite: ['Kipphan, 2001'] }) });
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS)), concepts), /cites "Kipphan, 2001", which is not in the lesson's References/);
});

test('fails: a cite with no <Cite> marker in the text (CT-2)', () => {
  const concept = goodConcept();
  concept.body = 'A digital photo is a grid of pixels.';
  failsWith(conceptErrors(concept, ALL_FILES), /has no <Cite c="Gonzalez & Woods, 2018" \/> marker/);
});

test('fails: a <Cite> marker that is not in the cite list (CT-2)', () => {
  const concept = goodConcept();
  concept.body += ' More<Cite c="Kipphan, 2001" />.';
  failsWith(conceptErrors(concept, ALL_FILES), /<Cite c="Kipphan, 2001" \/> is not in the cite list/);
});

test('fails: a citation written in brackets instead of a marker (CT-2)', () => {
  const concept = goodConcept();
  concept.body += ' (Gonzalez & Woods, 2018)';
  failsWith(conceptErrors(concept, ALL_FILES), /not in brackets/);
});

test("fails: a <Cite> in the lesson's text missing from its References (CT-2)", () => {
  const source = lessonSource(GOOD_SCREENS).replace('</TryStep>', 'See<Cite c="Kipphan, 2001" />.\n</TryStep>');
  failsWith(lessonErrors(lesson(source), library()), /<Cite c="Kipphan, 2001" \/> is not in the lesson's References/);
});

test('fails: no Sources list, or one before Wrap up (CT-2)', () => {
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS).replace(' data-sources=""', '')), library()), /0 Sources lists/);
  const early = `<ol data-sources=""><li>x</li></ol>\n${lessonSource(GOOD_SCREENS).replace(' data-sources=""', '')}`;
  failsWith(lessonErrors(lesson(early), library()), /must be inside Wrap up/);
});

test('fails: the Sources label count differs from the list (CT-2)', () => {
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS).replace('Sources (1)', 'Sources (4)')), library()), /label says 4, the list has 1/);
});

// ---------- notes on a step (SN-1) ----------

const withNote = (note, cell = '<Cell file="a.py" check />') =>
  lessonSource(GOOD_SCREENS.replace('concept="a">\n</TryStep>', `concept="a">\n${note}\n${cell}\n</TryStep>`));
const WATCH = '<Theory slot="theory" title="Watch out" line="line 4">x</Theory>';
const WORKED = '<Theory slot="after" title="Why it worked" line="lines 7 and 9">x</Theory>';

test('a Watch out and a Why it worked, each with a code line and a check, pass (SN-1)', () => {
  assert.deepEqual(lessonErrors(lesson(withNote(WATCH + WORKED)), library()), []);
});

test('fails: two Watch out notes on one step (SN-1)', () => {
  failsWith(lessonErrors(lesson(withNote(WATCH + WATCH)), library()), /2 Watch out notes, at most 1/);
});

test('fails: Why it worked on a step with no check (SN-1)', () => {
  failsWith(lessonErrors(lesson(withNote(WORKED, '<Cell file="a.py" />')), library()), /no check to open it after/);
});

test('fails: a note with no code line, a wrong title or no slot (SN-1)', () => {
  failsWith(lessonErrors(lesson(withNote('<Theory slot="theory" title="Watch out">x</Theory>')), library()), /names no code line/);
  failsWith(lessonErrors(lesson(withNote('<Theory slot="theory" title="Pitfall" line="line 4">x</Theory>')), library()), /must be titled "Watch out"/);
  failsWith(lessonErrors(lesson(withNote('<Theory title="Idea" line="line 4">x</Theory>')), library()), /note in no known slot/);
});

// ---------- each lesson rule ----------

test('fails: more than 4 concept screens (FW-1)', () => {
  const screens = ['a', 'b', 'c', 'd', 'e'].map((id, i) => `<ConceptScreen id="${id}" n={${i + 1}} of={5} minutes={1} />
<TryStep n={${i + 1}} kind="write" title="x" minutes={1} concept="${id}">
</TryStep>`).join('\n');
  const source = lessonSource(screens, '<TryWrap minutes={1} recall={["a", "b", "c", "d", "e"]}>');
  failsWith(lessonErrors(lesson(source), library()), /5 concept screens, over 4/);
});

test('fails: two concept screens in a row (condition 1)', () => {
  const source = lessonSource(GOOD_SCREENS.replace('<TryStep n={1} kind="predict" title="x" minutes={3} concept="a">\n</TryStep>\n', ''));
  failsWith(lessonErrors(lesson(source), library()), /concepts "a" and "b" are in a row/);
});

test('fails: a concept screen before Make it first (condition 1)', () => {
  const source = `<ConceptScreen id="a" n={1} of={1} minutes={1} />\n<MakeItFirst title="x" minutes={3}>\n</MakeItFirst>\n<TryStep n={1} kind="write" title="x" minutes={3} concept="a">\n</TryStep>\n<TryWrap minutes={3} recall={["a"]}>\n${REFS}\n</TryWrap>`;
  failsWith(lessonErrors(lesson(source), library()), /comes before Make it first/);
});

test('fails: a concept screen with no task after it (condition 1)', () => {
  const source = lessonSource(GOOD_SCREENS.replace('<TryStep n={3} kind="fix" title="x" minutes={3} concept="c">\n</TryStep>', ''));
  failsWith(lessonErrors(lesson(source), library()), /concept "c" has no task step after it/);
});

test('fails: a step whose concept has no screen before it and no Earlier link (condition 3)', () => {
  const source = lessonSource(GOOD_SCREENS.replace('concept="c"', 'concept="d"'));
  failsWith(lessonErrors(lesson(source), library()), /step 3 uses "d" with no concept screen before it and no Earlier link/);
});

test('passes condition 3 with an Earlier link: a concept introduced in an earlier lesson', () => {
  const concepts = library({ d: goodConcept('d', { introduced: { lesson: 'w1-see/1.1.1' } }) });
  const source = lessonSource(GOOD_SCREENS.replace('concept="c"', 'concept="d"'));
  assert.ok(!lessonErrors(lesson(source), concepts).some((error) => /condition 3/.test(error)));
});

test('fails: a step that names no concept (condition 3)', () => {
  const source = lessonSource(GOOD_SCREENS.replace(' concept="b"', ''));
  failsWith(lessonErrors(lesson(source), library()), /step 2 names no concept/);
});

test('fails: more than one interactive figure (FW-6)', () => {
  const interactive = (id) => {
    const concept = goodConcept(id);
    concept.data.figure.kind = 'interactive';
    return concept;
  };
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS)), library({ a: interactive('a'), b: interactive('b') })), /2 interactive figures, at most 1/);
});

test('fails: an unknown concept id', () => {
  const source = lessonSource(GOOD_SCREENS.replace('id="b"', 'id="nope"').replace('concept="b"', 'concept="nope"'));
  failsWith(lessonErrors(lesson(source), library()), /unknown concept id "nope"/);
});

test('fails: minutes over the lesson budget (/try: 15)', () => {
  const source = lessonSource(GOOD_SCREENS.replace('kind="fix" title="x" minutes={3}', 'kind="fix" title="x" minutes={4}'));
  failsWith(lessonErrors(lesson(source), library()), /16 min, over the lesson budget of 15/);
});

test('fails: an own-words task in Wrap up (TRB-2: recall only)', () => {
  const source = lessonSource(GOOD_SCREENS).replace('</TryWrap>', '<Task slot="task" label="In your own words">Why?</Task></TryWrap>');
  failsWith(lessonErrors(lesson(source), library()), /Wrap up has a <Task>; Wrap up is recall only/);
});

test('fails: recall repeats the prediction question', () => {
  const concept = goodConcept();
  concept.data.recall = question();
  failsWith(conceptErrors(concept, ALL_FILES), /recall repeats the prediction question/);
});

test('fails: a public page using a concept figure under /workshop-media/ (TRB-3 a)', () => {
  const gated = goodConcept('a');
  gated.data.figure.folder = '/workshop-media/concepts/fig';
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS)), library({ a: gated })), /public page uses concept "a", whose figure is under \/workshop-media\//);
  assert.ok(!lessonErrors(lesson(lessonSource(GOOD_SCREENS), { public: false }), library({ a: gated })).some((e) => /workshop-media/.test(e)));
});

test('fails: Wrap up recall not matching the concept screens (FW-3)', () => {
  const source = lessonSource(GOOD_SCREENS, '<TryWrap minutes={3} recall={["a", "c"]}>');
  failsWith(lessonErrors(lesson(source), library()), /Wrap up recall \[a, c\] must list the concept screens in order \[a, b, c\]/);
});

// ---------- Go further (GF-2, framework 03e §14: GFR-1 to GFR-7; one screen per task) ----------

const task = (n, count, extra = '') => `
<GoFurther n={${n}} of={${count}} kind="Extend" title="x">
<Task slot="task">
1. Run the code.
2. Add one line.
</Task>
<Diagram name="t" alt="x" caption="x" />
<Hint>Look above.</Hint>
<Hint kind="solution">One line.</Hint>
${extra}
<Cell slot="work" file="f.py" source="s${n}.py" solution="s${n + 1}.py" chain="c" label="task ${n}" solutionCode />
</GoFurther>`;
const furtherRun = (count = 1, extra = '') => [1, 2, 3, 4].slice(0, count).map((n) => task(n, count, extra)).join('\n');
const BRANCH_WRAP = '<TryWrap minutes={2} recall={["a", "b", "c"]} branch>';
// The cell the run continues from (the lesson's last step), with the same chain.
const CHAIN_STEP = '<Cell slot="work" file="s3.py" check solution="s1.py" chain="c" label="step 3" />';
const withFurther = (run, wrap = BRANCH_WRAP) => lessonSource(GOOD_SCREENS + CHAIN_STEP, wrap) + run;

test('a lesson with a valid Go further run passes; one without it passes too (optional)', () => {
  assert.deepEqual(lessonErrors(lesson(withFurther(furtherRun(3))), library()), []);
  assert.deepEqual(lessonErrors(lesson(lessonSource(GOOD_SCREENS)), library()), []);
});

test('fails: Wrap up without the branch prop (GFR-1)', () => {
  failsWith(lessonErrors(lesson(withFurther(furtherRun(1), '<TryWrap minutes={2} recall={["a", "b", "c"]}>')), library()), /needs the "branch" prop/);
});

test('fails: Go further before Wrap up (GFR-1)', () => {
  const source = lessonSource(GOOD_SCREENS, BRANCH_WRAP).replace('<TryWrap', `${furtherRun(1)}\n<TryWrap`);
  failsWith(lessonErrors(lesson(source), library()), /must come after Wrap up/);
});

test('fails: four Go further tasks, or numbering that does not match (GFR-1)', () => {
  failsWith(lessonErrors(lesson(withFurther(furtherRun(4))), library()), /4 tasks, 1 to 3/);
  failsWith(lessonErrors(lesson(withFurther(furtherRun(2).replace('n={2} of={2}', 'n={3} of={2}'))), library()), /must be n=\{2\} of=\{2\}/);
});

test('fails: a task with no target picture, no hint or no solution (GFR-4, GFR-5)', () => {
  const run = furtherRun(1);
  failsWith(lessonErrors(lesson(withFurther(run.replace('<Diagram name="t" alt="x" caption="x" />', ''))), library()), /no target picture/);
  failsWith(lessonErrors(lesson(withFurther(run.replace('<Hint>', '<Hint kind="note">'))), library()), /no hint/);
  failsWith(lessonErrors(lesson(withFurther(run.replace('<Hint kind="solution">', '<Hint kind="note">'))), library()), /no <Hint kind="solution">/);
});

test('fails: a task over 40 words (GFR-4)', () => {
  const long = 'word '.repeat(41);
  failsWith(lessonErrors(lesson(withFurther(furtherRun(1).replace('2. Add one line.', long))), library()), /task is \d+ words, at most 40/);
});

test('fails: a task with no cell, or a cell with a check (GFR-4, GFR-5)', () => {
  failsWith(lessonErrors(lesson(withFurther(furtherRun(1).replace('slot="work"', 'slot="other"'))), library()), /no <Cell slot="work">/);
  failsWith(lessonErrors(lesson(withFurther(furtherRun(1).replace('file="f.py"', 'file="f.py" check'))), library()), /has a check/);
});

test('fails: a deeper link on a public page; allowed on a workshop lesson (GFR-7, WS-13)', () => {
  const source = withFurther(furtherRun(1, '<a class="wb-deeper">Go deeper</a>'));
  failsWith(lessonErrors(lesson(source), library()), /deeper link/);
  assert.ok(!lessonErrors(lesson(source, { public: false }), library()).some((error) => /deeper/.test(error)));
});

test('fails: Wrap up has the branch prop but the lesson has no Go further (GFR-1)', () => {
  failsWith(lessonErrors(lesson(lessonSource(GOOD_SCREENS, BRANCH_WRAP)), library()), /no <GoFurther>/);
});

test('fails: a Go further cell that does not continue the code before it (GFC-2, GFC-4)', () => {
  const run = furtherRun(2);
  failsWith(lessonErrors(lesson(withFurther(run.replace(' chain="c"', ''))), library()), /cell has no chain=/);
  failsWith(lessonErrors(lesson(withFurther(run.replace(' source="s1.py"', ''))), library()), /cell has no source=/);
  failsWith(lessonErrors(lesson(withFurther(run.replace(' solution="s2.py"', ''))), library()), /cell has no solution=/);
  failsWith(lessonErrors(lesson(withFurther(run.replace(' label="task 1"', ''))), library()), /cell has no label=/);
  failsWith(lessonErrors(lesson(withFurther(run.replace(' solutionCode', ''))), library()), /no solutionCode/);
});

test('fails: the tasks use two chains or two file names, or nothing before them has the chain (GFC-3, GFR-4)', () => {
  const run = furtherRun(2);
  failsWith(lessonErrors(lesson(withFurther(run.replace('chain="c" label="task 2"', 'chain="d" label="task 2"'))), library()), /2 different chains/);
  failsWith(lessonErrors(lesson(withFurther(run.replace('file="f.py" source="s2.py"', 'file="g.py" source="s2.py"'))), library()), /2 different file names/);
  const orphan = lessonSource(GOOD_SCREENS, BRANCH_WRAP) + run;
  failsWith(lessonErrors(lesson(orphan), library()), /no cell before Go further has chain="c"/);
});

test('fails: a task whose source is not the solution before it (GFC-2)', () => {
  failsWith(lessonErrors(lesson(withFurther(furtherRun(2).replace('source="s2.py"', 'source="other.py"'))), library()), /starts from other\.py/);
});
