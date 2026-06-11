// One-off: apply the 2026-06 content restructure from restructure-manifest.json.
//
// Phase 1 — git mv each lesson MDX into the v1-mirrored module/subtopic tree.
// Phase 2 — git mv each public/lessons/<id>/ dir to public/lesson-media/<...>/.
// Phase 3 — rewrite asset refs inside the moved MDX: "/lessons/<id>/<file>"
//           becomes the new "/lesson-media/<...>/<file>" URL. Bare
//           "/lessons/<id>" page links are left untouched (URLs are stable).
// Phase 4 — report every remaining "/lessons/" occurrence for eyeball review
//           (expected: cross-lesson page links only).
//
// Idempotent-ish: phases skip moves whose source no longer exists.

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { ROOT } from '../lib/catalog.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(fs.readFileSync(path.join(__dirname, 'restructure-manifest.json'), 'utf8'));

const git = (...args) => execFileSync('git', args, { cwd: ROOT, stdio: 'pipe' });

// ---- Phase 1 + 2: moves ----------------------------------------------------
let movedMdx = 0;
let movedAssets = 0;
for (const e of manifest.entries) {
  const oldMdx = path.join(ROOT, e.oldMdx);
  const newMdx = path.join(ROOT, e.newMdx);
  if (fs.existsSync(oldMdx)) {
    fs.mkdirSync(path.dirname(newMdx), { recursive: true });
    git('mv', e.oldMdx, e.newMdx);
    movedMdx++;
  }
  const oldDir = path.join(ROOT, e.oldAssetDir);
  const newDir = path.join(ROOT, e.newAssetDir);
  if (fs.existsSync(oldDir)) {
    fs.mkdirSync(path.dirname(newDir), { recursive: true });
    git('mv', e.oldAssetDir, e.newAssetDir);
    movedAssets++;
  }
}
console.log(`moved ${movedMdx} MDX files, ${movedAssets} asset dirs`);

// ---- Phase 3: rewrite asset refs -------------------------------------------
const urlById = new Map(manifest.entries.map((e) => [e.id, e.newAssetUrl]));
// "/lessons/<id>/" followed by a path segment = asset ref. The lookahead
// excludes bare page links ("/lessons/2.1.1" or "/lessons/2.1.1/").
const ASSET_REF = /\/lessons\/(\d+(?:\.\d+)*)\/(?=[A-Za-z0-9_.-])/g;

let rewrites = 0;
const unknownIds = new Set();
for (const e of manifest.entries) {
  const file = path.join(ROOT, e.newMdx);
  const before = fs.readFileSync(file, 'utf8');
  const after = before.replace(ASSET_REF, (m, id) => {
    const url = urlById.get(id);
    if (!url) {
      unknownIds.add(`${e.id} -> ${id}`);
      return m;
    }
    rewrites++;
    return url;
  });
  if (after !== before) fs.writeFileSync(file, after);
}
console.log(`rewrote ${rewrites} asset refs`);
if (unknownIds.size) console.log(`UNMAPPED asset ids (review!): ${[...unknownIds].join(', ')}`);

// ---- Phase 4: leftover /lessons/ occurrences -------------------------------
const leftovers = [];
const walk = (dir) => {
  for (const d of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) walk(p);
    else if (d.name.endsWith('.mdx')) {
      const lines = fs.readFileSync(p, 'utf8').split('\n');
      lines.forEach((line, i) => {
        if (line.includes('/lessons/')) {
          leftovers.push(`${path.relative(ROOT, p)}:${i + 1}: ${line.trim().slice(0, 120)}`);
        }
      });
    }
  }
};
walk(path.join(ROOT, 'src', 'content', 'lessons'));
console.log(`\nremaining "/lessons/" mentions (should be page links only): ${leftovers.length}`);
for (const l of leftovers) console.log(`  ${l}`);
