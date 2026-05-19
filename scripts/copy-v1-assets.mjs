// ============================================================
//  copy-v1-assets.mjs
//  Data-driven asset migration. Reads thesis_automation/reports/
//  migration-inventory.json and copies top-level lesson assets
//  into public/lessons/<slug>/.
//
//  Conservative by default:
//    - Copies only TOP-LEVEL files from each v1 leaf folder
//      (skipping README.rst, dotfiles, and the usual cruft)
//    - Drops files larger than MAX_FILE_BYTES (25 MB default)
//    - Does NOT recurse into subdirectories
//
//  This avoids accidentally pulling in training datasets, model
//  caches, lightning_logs, etc. that v1 lesson folders sometimes
//  contain. Lessons that genuinely need a subdir (e.g. visuals/
//  for diagram-generation scripts) can opt in via PER_LESSON
//  below.
//
//  Usage:
//    npm run copy-assets                          # all lessons
//    npm run copy-assets -- --only=1.1.1,4.1.1    # subset by slug
//    V1_ROOT=/path/to/numpy-to-genAI npm run copy-assets
//
//  v1 is treated as read-only — this script only reads from it.
//  Idempotent: re-running overwrites destination files.
// ============================================================

import { promises as fs } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const V2_ROOT = resolve(__dirname, '..');
const V1_ROOT =
  process.env.V1_ROOT || resolve(V2_ROOT, '..', 'numpy-to-genAI');
const INVENTORY_PATH = join(
  V2_ROOT,
  'thesis_automation',
  'reports',
  'migration-inventory.json'
);
const DEST_ROOT = join(V2_ROOT, 'public', 'lessons');

// Per-file size cap. Any single file larger than this is skipped
// with a warning. Catches stray model weights / very large GIFs.
const MAX_FILE_BYTES = 25 * 1024 * 1024; // 25 MB

// File extensions to copy. README.rst is intentionally excluded — the MDX
// hand-port is canonical. Model weights (.pth) are excluded unless a lesson
// opts in via PER_LESSON.includePth.
const KEEP_EXT = new Set([
  '.png',
  '.gif',
  '.jpg',
  '.jpeg',
  '.svg',
  '.py',
  '.txt',
]);

// Files to always skip.
const SKIP_FILE_NAMES = new Set([
  '.DS_Store',
  'Thumbs.db',
  'README.rst',
  'README.md',
]);

// Per-lesson configuration. Empty by default — every lesson uses the
// conservative top-level-only defaults. Add an entry when a specific lesson
// needs subdirectory recursion or .pth inclusion.
const PER_LESSON = {
  // Lessons that need their visuals/ subdir copied alongside top-level
  // assets. Diagram-generation assets (theory GIFs, expected outputs)
  // live under visuals/ in the v1 source tree.
  '1.2.2': { includeSubdirs: ['visuals'] },
  '12.1.2': { includePth: true },
};

// Default option set.
function optionsFor(slug) {
  const cfg = PER_LESSON[slug] || {};
  return {
    includeSubdirs: cfg.includeSubdirs || [],
    includePth: !!cfg.includePth,
  };
}

// ---------------------------------------------------------------
// Copy every keep-eligible file directly inside `src` (no recursion)
// into `<DEST_ROOT>/<slug>/`. Returns counts.
// ---------------------------------------------------------------
async function copyDirFlat(srcDir, destDir, { allowPth }) {
  const stat = { copied: 0, skippedExt: 0, skippedSize: 0, skippedName: 0 };
  let entries;
  try {
    entries = await fs.readdir(srcDir, { withFileTypes: true });
  } catch (err) {
    if (err.code !== 'ENOENT') console.error(`  [error] ${srcDir}: ${err.message}`);
    return stat;
  }
  for (const entry of entries) {
    if (!entry.isFile()) continue;
    const name = entry.name;
    if (SKIP_FILE_NAMES.has(name) || name.startsWith('.')) {
      stat.skippedName += 1;
      continue;
    }
    const ext = name.slice(name.lastIndexOf('.')).toLowerCase();
    if (ext === '.pth') {
      if (!allowPth) {
        stat.skippedExt += 1;
        continue;
      }
    } else if (!KEEP_EXT.has(ext)) {
      stat.skippedExt += 1;
      continue;
    }
    const srcPath = join(srcDir, name);
    let stats;
    try {
      stats = await fs.stat(srcPath);
    } catch {
      continue;
    }
    if (stats.size > MAX_FILE_BYTES) {
      console.error(
        `  [skip] ${srcPath} too large: ${(stats.size / 1024 / 1024).toFixed(1)} MB`
      );
      stat.skippedSize += 1;
      continue;
    }
    const dstPath = join(destDir, name);
    await fs.mkdir(dirname(dstPath), { recursive: true });
    await fs.copyFile(srcPath, dstPath);
    stat.copied += 1;
  }
  return stat;
}

// ---------------------------------------------------------------
// Process a single lesson.
// ---------------------------------------------------------------
async function copyLesson(entry, opts) {
  const slug = entry.leafId;
  const srcDir = join(V1_ROOT, entry.v1PathRelative);

  // Top-level copy.
  const top = await copyDirFlat(srcDir, join(DEST_ROOT, slug), {
    allowPth: opts.includePth,
  });

  // Opt-in subdirs (preserved as subdirs under public/lessons/<slug>/).
  const subStats = [];
  for (const subName of opts.includeSubdirs) {
    const subStat = await copyDirFlat(
      join(srcDir, subName),
      join(DEST_ROOT, slug, subName),
      { allowPth: opts.includePth }
    );
    subStats.push({ name: subName, ...subStat });
  }

  return { top, subStats };
}

// ---------------------------------------------------------------
function parseOnlyFlag() {
  const arg = process.argv.find((a) => a.startsWith('--only='));
  if (!arg) return null;
  return new Set(
    arg
      .slice('--only='.length)
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
  );
}

// ---------------------------------------------------------------
async function main() {
  console.log(`v2 root:    ${V2_ROOT}`);
  console.log(`v1 root:    ${V1_ROOT}`);
  console.log(`inventory:  ${INVENTORY_PATH}`);
  console.log(`max file:   ${(MAX_FILE_BYTES / 1024 / 1024).toFixed(0)} MB\n`);

  let inventory;
  try {
    inventory = JSON.parse(await fs.readFile(INVENTORY_PATH, 'utf8'));
  } catch {
    console.error(`Cannot read inventory at ${INVENTORY_PATH}`);
    console.error(`Run: node scripts/inventory-v1.mjs`);
    process.exit(1);
  }

  const only = parseOnlyFlag();
  if (only) console.log(`Filtering to slugs: ${[...only].join(', ')}\n`);

  let totalCopied = 0;
  let lessons = 0;
  let lessonsSkippedNoV1 = 0;
  let lessonsSkippedFilter = 0;

  for (const entry of inventory.entries) {
    const slug = entry.leafId;
    if (only && !only.has(slug)) {
      lessonsSkippedFilter += 1;
      continue;
    }
    if (!entry.v1Path) {
      lessonsSkippedNoV1 += 1;
      continue;
    }

    const opts = optionsFor(slug);
    const r = await copyLesson(entry, opts);
    const lessonCopied =
      r.top.copied + r.subStats.reduce((s, x) => s + x.copied, 0);
    const subSummary =
      r.subStats.length > 0
        ? ' [' +
          r.subStats
            .map((x) => `${x.name}:${x.copied}`)
            .join(',') +
          ']'
        : '';
    console.log(
      `→ ${slug.padEnd(8)} ${entry.tier.padEnd(8)} top:${r.top.copied} files (${r.top.skippedExt}+${r.top.skippedSize}+${r.top.skippedName} skipped)${subSummary}`
    );
    totalCopied += lessonCopied;
    lessons += 1;
  }

  console.log('');
  console.log(`=== Summary ===`);
  console.log(`  Lessons processed:        ${lessons}`);
  console.log(`  Total files copied:       ${totalCopied}`);
  console.log(`  Lessons skipped (no v1):  ${lessonsSkippedNoV1}`);
  if (only)
    console.log(`  Lessons skipped (filter): ${lessonsSkippedFilter}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
