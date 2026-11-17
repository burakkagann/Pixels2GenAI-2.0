/**
 * Concept framework check (FW-5): every concept file in src/content/concepts/ and every lesson that uses
 * <ConceptScreen>. Run by `npm run check` and before every build; exits 1 on any error.
 * The rules live in src/lib/concepts/rules.mjs (the components throw on the same faults); tests: npm run test:concepts.
 *
 * Lessons checked:
 *   src/try/*.mdx                                 public (/try), budget 15 min (the public pages say 15; Kağan's test run, 16 Nov)
 *   src/content/workshop-lessons/<w>/<id>_*.mdx   gated, budget from the frontmatter duration (upper number)
 */
import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';
import { conceptErrors, lessonErrors, lessonMinutes } from '../src/lib/concepts/rules.mjs';

const ROOT = process.cwd();
const CONCEPTS = path.join(ROOT, 'src', 'content', 'concepts');
const exists = (relative) => fs.existsSync(path.join(ROOT, relative));

/** Frontmatter and body of an MDX file. */
function readMdx(text) {
  const match = text.replace(/\r\n/g, '\n').match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!match) return { data: {}, body: text };
  return { data: yaml.load(match[1]) ?? {}, body: match[2] };
}

const errors = [];
const concepts = new Map();
if (fs.existsSync(CONCEPTS)) {
  for (const file of fs.readdirSync(CONCEPTS).filter((f) => f.endsWith('.mdx')).sort()) {
    const id = file.replace(/\.mdx$/, '');
    let parsed;
    try {
      parsed = readMdx(fs.readFileSync(path.join(CONCEPTS, file), 'utf8'));
    } catch (error) {
      errors.push(`concept "${id}": frontmatter does not parse: ${error.message}`);
      continue;
    }
    concepts.set(id, parsed);
    errors.push(...conceptErrors({ id, ...parsed }, exists));
  }
}

const lessons = [];
const tryDir = path.join(ROOT, 'src', 'try');
for (const file of fs.readdirSync(tryDir).filter((f) => f.endsWith('.mdx'))) {
  lessons.push({ file: `src/try/${file}`, lesson: 'try', public: true, budget: 15 });
}
const workshopDir = path.join(ROOT, 'src', 'content', 'workshop-lessons');
if (fs.existsSync(workshopDir)) {
  for (const workshop of fs.readdirSync(workshopDir)) {
    const dir = path.join(workshopDir, workshop);
    if (!fs.statSync(dir).isDirectory()) continue;
    for (const file of fs.readdirSync(dir).filter((f) => f.endsWith('.mdx'))) {
      const relative = `src/content/workshop-lessons/${workshop}/${file}`;
      const { data } = readMdx(fs.readFileSync(path.join(ROOT, relative), 'utf8'));
      const numbers = String(data.duration ?? '').match(/\d+/g);
      lessons.push({ file: relative, lesson: `${workshop}/${file.match(/^[\d.]+/)?.[0] ?? file}`, public: false,
        budget: numbers ? Number(numbers[numbers.length - 1]) : 45 });
    }
  }
}

const report = [];
for (const lesson of lessons) {
  const source = fs.readFileSync(path.join(ROOT, lesson.file), 'utf8');
  const found = lessonErrors({ ...lesson, source }, concepts);
  errors.push(...found);
  if (source.includes('<ConceptScreen')) report.push(`${lesson.file}: ${lessonMinutes(source)} min`);
}

console.log(`\nConcept check — ${concepts.size} concepts, ${report.length} lesson(s) using them`);
for (const line of report) console.log(`  · ${line}`);
for (const error of errors) console.error(`  x ${error}`);
if (errors.length) {
  console.error(`\nFAILED — ${errors.length} error(s).\n`);
  process.exit(1);
}
console.log('\nOK — 0 errors.\n');
