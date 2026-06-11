/**
 * Lesson catalog integrity check.
 *
 * Run standalone (`npm run check`) or automatically before every build
 * (wired into the "build" script). Fails the build (exit 1) on any ERROR.
 *
 * ERRORS (break the site):
 *   - a `lessonSlug` in subtopics.ts with no matching MDX file
 *   - a `firstLesson` in modules.ts with no matching MDX file
 *   - an asset referenced by a lesson (/lesson-media/…) missing from public/
 *   - a legacy "/lessons/<id>/<file>" asset reference (pre-restructure form)
 *   - the same slug wired to more than one leaf
 *
 * WARNINGS (intentional in-progress states — never fail):
 *   - an MDX file that exists but is not yet wired into subtopics.ts
 *   - a module whose firstLesson is not among its own wired leaves
 */

import fs from 'node:fs';
import {
  buildModuleView,
  readLessonFiles,
  lessonFilePath,
  publicAssetPath,
} from './lib/catalog.mjs';

const errors = [];
const warnings = [];

const view = buildModuleView();
const allLeaves = view.flatMap((m) => m.leaves.map((l) => ({ ...l, mIdx: m.idx })));
const files = readLessonFiles();

// 1. Wired slug -> MDX must exist; collect slug -> [leafIds] for dup check.
const slugUsage = new Map();
for (const leaf of allLeaves) {
  if (!leaf.slug) continue;
  if (!slugUsage.has(leaf.slug)) slugUsage.set(leaf.slug, []);
  slugUsage.get(leaf.slug).push(`${leaf.mIdx}:${leaf.id}`);
  if (!leaf.hasFile) {
    errors.push(
      `Leaf ${leaf.id} (M ${leaf.mIdx}) wires lessonSlug "${leaf.slug}" but no MDX with that id exists under src/content/lessons/.`
    );
  }
}

// 1b. Duplicate slug wiring.
for (const [slug, users] of slugUsage) {
  if (users.length > 1) {
    errors.push(`lessonSlug "${slug}" is wired to multiple leaves: ${users.join(', ')}.`);
  }
}

// 2. Orphan MDX (exists but not wired) -> warning.
const wiredSlugs = new Set([...slugUsage.keys()]);
for (const file of files) {
  if (!wiredSlugs.has(file)) {
    warnings.push(
      `MDX lesson "${file}" exists but is not wired into subtopics.ts (renders as "Coming soon"; add lessonSlug to ship it).`
    );
  }
}

// 3. firstLesson sanity.
for (const m of view) {
  if (!m.firstLesson) continue;
  if (!lessonFilePath(m.firstLesson)) {
    errors.push(
      `Module ${m.idx} firstLesson "${m.firstLesson}" has no MDX file under src/content/lessons/.`
    );
  }
  const inModule = m.leaves.some((l) => l.slug === m.firstLesson);
  if (!inModule) {
    warnings.push(
      `Module ${m.idx} firstLesson "${m.firstLesson}" is not wired to any leaf in this module's subtopics.`
    );
  }
}

// 4. Asset references inside each shipped MDX must resolve under public/.
//    "/lessons/<id>" (no trailing path) is a page link; assets live under
//    "/lesson-media/…". A "/lessons/<id>/<file>" form is a stale
//    pre-restructure asset path and fails the build.
const ASSET_RE = /(?:src|href)\s*=\s*["'](\/lesson-media\/[^"']+)["']/g;
const LEGACY_ASSET_RE = /["'](\/lessons\/[^"']+\/[^"']+)["']/g;
const LESSON_LINK_RE = /(?:src|href)\s*=\s*["']\/lessons\/([^/"']+)\/?["']/g;
for (const slug of wiredSlugs) {
  const file = lessonFilePath(slug);
  if (!file) continue; // already reported as error above
  const content = fs.readFileSync(file, 'utf8');

  for (const match of content.matchAll(ASSET_RE)) {
    const ref = match[1];
    const abs = publicAssetPath(ref);
    if (!fs.existsSync(abs)) {
      errors.push(`Lesson "${slug}" references missing asset: ${ref}`);
    }
  }

  for (const match of content.matchAll(LEGACY_ASSET_RE)) {
    errors.push(`Lesson "${slug}" uses a legacy asset path: ${match[1]} (assets now live under /lesson-media/).`);
  }

  for (const match of content.matchAll(LESSON_LINK_RE)) {
    const target = match[1];
    if (!wiredSlugs.has(target) && !lessonFilePath(target)) {
      warnings.push(`Lesson "${slug}" links to /lessons/${target} which is not a shipped lesson.`);
    }
  }
}

// ---- Report -------------------------------------------------------------
const shippedCount = view.reduce((n, m) => n + m.shipped.length, 0);
const wiredCount = view.reduce((n, m) => n + m.wired.length, 0);
const leafCount = view.reduce((n, m) => n + m.leaves.length, 0);

console.log('');
console.log(`Lesson check — ${shippedCount} shipped / ${wiredCount} wired / ${leafCount} total leaves`);

for (const w of warnings) console.log(`  ! ${w}`);
for (const e of errors) console.error(`  x ${e}`);

if (errors.length) {
  console.error(`\nFAILED — ${errors.length} error(s), ${warnings.length} warning(s).\n`);
  process.exit(1);
}
console.log(`\nOK — 0 errors, ${warnings.length} warning(s).\n`);
