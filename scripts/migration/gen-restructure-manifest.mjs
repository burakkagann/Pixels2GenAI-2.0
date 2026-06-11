// One-off: generate the rename manifest for the 2026-06 content restructure.
//
// Maps every flat lesson (src/content/lessons/<id>.mdx + public/lessons/<id>/)
// to its v1-mirrored destination:
//   src/content/lessons/<Module_NN_name>/<N.M_subtopic>/<N.M.K_leaf>.mdx
//   public/lesson-media/<Module_NN_name>/<N.M_subtopic>/<N.M.K_leaf>/
//
// Folder names are copied verbatim from the v1 tree (read-only). Leaves with
// no v1 folder fall back to a snake_case of their catalog title and are
// flagged in the manifest for review.
//
// Output: scripts/migration/restructure-manifest.json

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { readSubtopics, ROOT } from '../lib/catalog.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const V1_CONTENT = 'C:/Users/User/Desktop/git-repos/numpy-to-genAI/content';
const LESSONS_DIR = path.join(ROOT, 'src', 'content', 'lessons');

// ---- v1 tree index --------------------------------------------------------
// moduleDirs: "02" -> "Module_02_geometry_mathematics"
// leafDirs:   "2.1.1" -> { sub: "2.1_basic_shapes_primitives", leaf: "2.1.1_lines" }
const moduleDirs = new Map();
const leafDirs = new Map();

for (const mod of fs.readdirSync(V1_CONTENT, { withFileTypes: true })) {
  if (!mod.isDirectory()) continue;
  const m = mod.name.match(/^Module_(\d{2})_/);
  if (!m) continue;
  moduleDirs.set(m[1], mod.name);
  const modPath = path.join(V1_CONTENT, mod.name);
  for (const sub of fs.readdirSync(modPath, { withFileTypes: true })) {
    if (!sub.isDirectory()) continue;
    if (!/^\d+\.\d+_/.test(sub.name)) continue;
    const subPath = path.join(modPath, sub.name);
    for (const leaf of fs.readdirSync(subPath, { withFileTypes: true })) {
      if (!leaf.isDirectory()) continue;
      const lm = leaf.name.match(/^(\d+\.\d+\.\d+)_/);
      if (!lm) continue;
      leafDirs.set(lm[1], { sub: sub.name, leaf: leaf.name });
    }
  }
}

// ---- catalog titles (fallback naming) -------------------------------------
const subtopics = readSubtopics();
const titleById = new Map();
const subTitleById = new Map();
for (const subs of Object.values(subtopics)) {
  for (const s of subs) {
    for (const l of s.leaves) {
      titleById.set(l.id, l.title);
      subTitleById.set(l.id, { subId: s.id, subTitle: s.title });
    }
  }
}

const snake = (s) =>
  s
    .toLowerCase()
    .replace(/&/g, ' ')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');

// ---- build manifest entries ------------------------------------------------
const ids = fs
  .readdirSync(LESSONS_DIR)
  .filter((f) => f.endsWith('.mdx'))
  .map((f) => f.replace(/\.mdx$/, ''))
  .sort((a, b) => {
    const pa = a.split('.').map(Number);
    const pb = b.split('.').map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
      if ((pa[i] ?? 0) !== (pb[i] ?? 0)) return (pa[i] ?? 0) - (pb[i] ?? 0);
    }
    return 0;
  });

const entries = [];
const fallbacks = [];

for (const id of ids) {
  const modIdx = id.split('.')[0].padStart(2, '0');
  const moduleDir = moduleDirs.get(modIdx);
  if (!moduleDir) throw new Error(`No v1 module folder for module ${modIdx} (lesson ${id})`);

  let subDir;
  let leafName;
  const hit = leafDirs.get(id);
  if (hit) {
    subDir = hit.sub;
    leafName = hit.leaf;
  } else {
    const meta = subTitleById.get(id);
    if (!meta) throw new Error(`Lesson ${id} not in v1 tree and not in subtopics.ts`);
    subDir = `${meta.subId}_${snake(meta.subTitle)}`;
    leafName = `${id}_${snake(titleById.get(id))}`;
    fallbacks.push(id);
  }

  const rel = `${moduleDir}/${subDir}`;
  entries.push({
    id,
    fromV1: Boolean(hit),
    oldMdx: `src/content/lessons/${id}.mdx`,
    newMdx: `src/content/lessons/${rel}/${leafName}.mdx`,
    oldAssetDir: `public/lessons/${id}`,
    newAssetDir: `public/lesson-media/${rel}/${leafName}`,
    oldAssetUrl: `/lessons/${id}/`,
    newAssetUrl: `/lesson-media/${rel}/${leafName}/`,
  });
}

const out = path.join(__dirname, 'restructure-manifest.json');
fs.writeFileSync(out, JSON.stringify({ generatedFor: 'content restructure', count: entries.length, fallbacks, entries }, null, 2));
console.log(`Wrote ${entries.length} entries to ${path.relative(ROOT, out)}`);
if (fallbacks.length) console.log(`Fallback-named (no v1 folder): ${fallbacks.join(', ')}`);
