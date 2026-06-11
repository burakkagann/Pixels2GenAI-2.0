/**
 * Lesson status report — `npm run status`.
 *
 * Prints a per-module table of shipped vs total leaves so the porting effort
 * (144+ remaining lessons) is visible at a glance. Read-only; never fails.
 */

import { buildModuleView, readLessonFiles } from './lib/catalog.mjs';

const view = buildModuleView();

const bar = (done, total, width = 14) => {
  if (!total) return ' '.repeat(width);
  const filled = Math.round((done / total) * width);
  return '#'.repeat(filled) + '.'.repeat(width - filled);
};

const pad = (s, n) => String(s).padEnd(n);
const padL = (s, n) => String(s).padStart(n);

console.log('');
console.log('  Pixels2GenAI · lesson status');
console.log('  ' + '-'.repeat(60));
console.log(
  '  ' + pad('Module', 26) + pad('Progress', 16) + padL('Ship', 7) + padL('Leaves', 8)
);
console.log('  ' + '-'.repeat(60));

let totShip = 0;
let totLeaves = 0;

for (const m of view) {
  const done = m.shipped.length;
  const total = m.leaves.length;
  totShip += done;
  totLeaves += total;
  const label = `M ${m.idx} ${m.title}`.slice(0, 25);
  const pct = total ? `${Math.round((done / total) * 100)}%` : '—';
  console.log(
    '  ' +
      pad(label, 26) +
      pad(bar(done, total), 16) +
      padL(`${done}`, 7) +
      padL(`${total}`, 8) +
      `   ${pct}`
  );

  // Show the wired-but-missing or shipped slugs inline when there are any.
  const issues = m.wired.filter((l) => !l.hasFile);
  if (issues.length) {
    for (const l of issues) {
      console.log(`        ! ${l.id} wired to "${l.slug}" — MDX missing`);
    }
  }
}

console.log('  ' + '-'.repeat(60));
const pct = totLeaves ? Math.round((totShip / totLeaves) * 100) : 0;
console.log(
  '  ' + pad('TOTAL', 26) + pad(bar(totShip, totLeaves), 16) + padL(`${totShip}`, 7) + padL(`${totLeaves}`, 8) + `   ${pct}%`
);

// Orphan MDX files (exist but unwired) — flagged so they aren't forgotten.
const wired = new Set(view.flatMap((m) => m.wired.map((l) => l.slug)));
const orphans = readLessonFiles().filter((f) => !wired.has(f));
if (orphans.length) {
  console.log('');
  console.log('  Unwired MDX (drop a lessonSlug into subtopics.ts to ship):');
  for (const o of orphans) console.log(`    - ${o}`);
}
console.log('');
