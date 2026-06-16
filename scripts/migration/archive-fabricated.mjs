/**
 * One-shot: archive the 91 fabricated lessons (generated during migration from
 * v1 stubs) out of the live tree without deleting them.
 *
 * For each slug it:
 *   - moves src/content/lessons/<rel>.mdx        -> archive/fabricated-lessons/<rel>.mdx
 *   - moves public/lesson-media/<rel>/  (assets) -> archive/fabricated-lessons/<rel>/
 *   - strips `, lessonSlug: '<slug>'` from src/data/curriculum/subtopics.ts
 *   - clears Module 07's firstLesson in src/data/curriculum/modules.ts
 *
 * Idempotent-ish: already-moved files are reported as "skipped (gone)".
 * Authority for the list: docs/reports/fabricated-lessons-audit.md
 */
import fs from 'node:fs';
import path from 'node:path';
import { ROOT, lessonFilePath, lessonAssetLocation, readLessonFiles } from '../lib/catalog.mjs';

const DEMOTE = [
  '1.1.2', '1.2.3', '1.3.3', '1.3.4',
  '2.1.5', '2.3.1', '2.3.4',
  '3.2.4', '3.3.4',
  '4.1.4', '4.1.5', '4.2.2', '4.2.3', '4.2.4', '4.3.2', '4.3.3',
  '5.1.2', '5.1.3', '5.1.4', '5.2.2', '5.2.3', '5.3.2', '5.3.4', '5.3.5', '5.4.1', '5.4.2', '5.4.3', '5.4.4',
  '6.1.2', '6.1.3', '6.1.4', '6.2.1', '6.2.2', '6.2.3', '6.2.4', '6.3.1', '6.3.2', '6.3.3', '6.3.4', '6.4.1', '6.4.2', '6.4.3',
  '7.1.1', '7.1.2', '7.1.3', '7.2.1', '7.2.2', '7.2.3', '7.3.1', '7.3.2', '7.3.3', '7.4.1', '7.4.2', '7.4.3',
  '8.1.2', '8.1.3', '8.1.4', '8.2.3', '8.2.4', '8.3.3', '8.3.4', '8.4.1', '8.4.2',
  '9.3.1', '9.3.2', '9.3.3', '9.4.1', '9.4.2', '9.4.3',
  '10.1.3', '10.2.1', '10.2.3', '10.2.4', '10.3.1', '10.3.2', '10.3.3', '10.4.1', '10.4.2', '10.4.3',
  '11.1.2', '11.1.3', '11.1.4', '11.2.1', '11.2.2', '11.2.4', '11.3.1', '11.3.2', '11.3.3', '11.4.1', '11.4.2', '11.4.3',
];

const LESSONS_DIR = path.join(ROOT, 'src', 'content', 'lessons');
const ARCHIVE_DIR = path.join(ROOT, 'archive', 'fabricated-lessons');

readLessonFiles(); // prime the catalog cache from disk before we start moving

function moveInto(src, dest) {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.renameSync(src, dest);
}

let movedMdx = 0, movedAssets = 0, missing = [];

for (const slug of DEMOTE) {
  const mdx = lessonFilePath(slug);
  const assets = lessonAssetLocation(slug); // computed from cached path, ok after moves
  if (!mdx || !fs.existsSync(mdx)) { missing.push(slug); continue; }

  const rel = path.relative(LESSONS_DIR, mdx);           // Module_xx/x.y/x.y.z_name.mdx
  const relNoExt = rel.replace(/\.mdx?$/, '');

  moveInto(mdx, path.join(ARCHIVE_DIR, rel));
  movedMdx++;

  if (assets && fs.existsSync(assets.dir)) {
    moveInto(assets.dir, path.join(ARCHIVE_DIR, relNoExt));
    movedAssets++;
  }
}

// --- strip lessonSlug entries from subtopics.ts ---------------------------
const subPath = path.join(ROOT, 'src', 'data', 'curriculum', 'subtopics.ts');
let sub = fs.readFileSync(subPath, 'utf8');
let stripped = 0;
for (const slug of DEMOTE) {
  const needle = `, lessonSlug: '${slug}'`;
  if (sub.includes(needle)) { sub = sub.split(needle).join(''); stripped++; }
}
fs.writeFileSync(subPath, sub);

// --- clear Module 07 firstLesson -----------------------------------------
const modPath = path.join(ROOT, 'src', 'data', 'curriculum', 'modules.ts');
let mod = fs.readFileSync(modPath, 'utf8');
const before = mod;
mod = mod.replace(/, *firstLesson: '7\.1\.1'/, '');
fs.writeFileSync(modPath, mod);

console.log(`MDX moved:        ${movedMdx}/${DEMOTE.length}`);
console.log(`Asset dirs moved: ${movedAssets}`);
console.log(`lessonSlug stripped: ${stripped}`);
console.log(`M07 firstLesson cleared: ${before !== mod}`);
if (missing.length) console.log(`Missing (already gone?): ${missing.join(', ')}`);
