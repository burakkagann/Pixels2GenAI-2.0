// ============================================================
//  inventory-v1.mjs
//  Scan the v1 numpy-to-genAI repo, classify every leaf in v2's
//  curriculum catalog by completeness tier, and write the result
//  to thesis_automation/reports/migration-inventory.json.
//
//  Usage:
//    node scripts/inventory-v1.mjs                  # auto-detect v1 as sibling
//    V1_ROOT=/path/to/numpy-to-genAI node scripts/inventory-v1.mjs
//
//  v1 is treated as read-only — this script only reads.
//  Idempotent: re-running overwrites the JSON.
// ============================================================

import { promises as fs } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const V2_ROOT = resolve(__dirname, '..');
const V1_ROOT =
  process.env.V1_ROOT ||
  resolve(V2_ROOT, '..', 'numpy-to-genAI'); // default: sibling of v2

const SUBTOPICS_PATH = join(V2_ROOT, 'src', 'data', 'subtopics.ts');
const MODULES_PATH = join(V2_ROOT, 'src', 'data', 'modules.ts');
const OUTPUT_PATH = join(V2_ROOT, 'thesis_automation', 'reports', 'migration-inventory.json');

const V1_CONTENT = join(V1_ROOT, 'content');

// Asset extensions we count as "real" content.
const ASSET_EXTS = new Set(['.png', '.gif', '.jpg', '.jpeg', '.svg']);
const SCRIPT_EXTS = new Set(['.py']);
const DOC_NAME = 'README.rst';

// Completeness tier thresholds.
const COMPLETE_README_LINES = 100;
const COMPLETE_MIN_SCRIPTS = 2;
const COMPLETE_MIN_ASSETS = 1;

// ---------------------------------------------------------------
// 1. Parse subtopics.ts (regex — the structure is very regular)
// ---------------------------------------------------------------
async function parseSubtopics() {
  const src = await fs.readFile(SUBTOPICS_PATH, 'utf8');

  // Match a SUBTOPICS module block: '00': [ ... ],
  //                                  '15': [ ... ],
  const modules = {};
  const moduleBlockRe = /^\s*'(\d{2})':\s*\[(\s*[\s\S]*?)\n\s*\],$/gm;
  let mm;
  while ((mm = moduleBlockRe.exec(src))) {
    const modIdx = mm[1];
    const body = mm[2];
    const subtopics = [];

    // Each subtopic block:
    //   { id: '1.1', title: '...', leaves: [ ... ] },
    const subRe = /\{\s*id:\s*'([^']+)',\s*title:\s*'([^']+)',\s*leaves:\s*\[([\s\S]*?)\]\s*\},?/g;
    let sm;
    while ((sm = subRe.exec(body))) {
      const subId = sm[1];
      const subTitle = sm[2];
      const leavesBody = sm[3];

      // Each leaf:
      //   { id: '1.1.1', title: '...' }
      //   { id: '1.1.1', title: '...', lessonSlug: '1.1.1' }
      const leafRe = /\{\s*id:\s*'([^']+)',\s*title:\s*'([^']+)'(?:,\s*lessonSlug:\s*'([^']+)')?\s*\}/g;
      const leaves = [];
      let lm;
      while ((lm = leafRe.exec(leavesBody))) {
        leaves.push({
          id: lm[1],
          title: lm[2],
          lessonSlug: lm[3] || null,
        });
      }
      subtopics.push({ id: subId, title: subTitle, leaves });
    }
    modules[modIdx] = subtopics;
  }
  return modules;
}

async function parseModules() {
  const src = await fs.readFile(MODULES_PATH, 'utf8');
  // { idx: '00', title: 'Foundations', em: '& Definitions', fw: 'F2', cycle: 'I' },
  const mods = {};
  const re =
    /\{\s*idx:\s*'(\d{2})',\s*title:\s*'([^']+)',\s*em:\s*'([^']*)',\s*fw:\s*'([^']+)',\s*cycle:\s*'([^']+)'(?:,\s*firstLesson:\s*'([^']+)')?(?:,\s*capstone:\s*(true|false))?\s*\}/g;
  let m;
  while ((m = re.exec(src))) {
    mods[m[1]] = {
      idx: m[1],
      title: m[2],
      em: m[3],
      fw: m[4],
      cycle: m[5],
      firstLesson: m[6] || null,
      capstone: m[7] === 'true',
    };
  }
  return mods;
}

// ---------------------------------------------------------------
// 2. Build a flat list of every v1 leaf folder.
//    Walks: <V1_CONTENT>/Module_NN_*/<X.Y>_*/<X.Y.Z>_*/
// ---------------------------------------------------------------
async function indexV1Folders() {
  const byLeafId = new Map(); // leaf-id ("1.1.1") -> absolute folder path

  let moduleDirs;
  try {
    moduleDirs = await fs.readdir(V1_CONTENT, { withFileTypes: true });
  } catch (err) {
    console.error(`Cannot read v1 content directory: ${V1_CONTENT}`);
    throw err;
  }

  for (const md of moduleDirs) {
    if (!md.isDirectory()) continue;
    if (!md.name.startsWith('Module_')) continue;

    const moduleDir = join(V1_CONTENT, md.name);
    const subDirs = await fs.readdir(moduleDir, { withFileTypes: true });

    for (const sd of subDirs) {
      if (!sd.isDirectory()) continue;
      // Subtopic folders look like "1.1_grayscale_color_basics"
      const subMatch = sd.name.match(/^(\d+\.\d+)_/);
      if (!subMatch) continue;

      const subDir = join(moduleDir, sd.name);
      const leafDirs = await fs.readdir(subDir, { withFileTypes: true });

      for (const ld of leafDirs) {
        if (!ld.isDirectory()) continue;
        // Leaf folders look like "1.1.1_color_basics"
        const leafMatch = ld.name.match(/^(\d+\.\d+\.\d+)_/);
        if (!leafMatch) continue;

        const leafId = leafMatch[1];
        const leafPath = join(subDir, ld.name);
        if (byLeafId.has(leafId)) {
          console.warn(`[warn] Duplicate v1 folder for leaf ${leafId}:`);
          console.warn(`       existing: ${byLeafId.get(leafId)}`);
          console.warn(`       new:      ${leafPath}`);
        } else {
          byLeafId.set(leafId, leafPath);
        }
      }
    }
  }

  return byLeafId;
}

// ---------------------------------------------------------------
// 3. Classify a single leaf folder.
//    Walks recursively to count READMEs, scripts, and images.
// ---------------------------------------------------------------
async function classifyLeafFolder(absPath) {
  const stat = { readmeLines: 0, scripts: 0, assets: 0, dirs: 0, files: 0 };

  async function walk(p) {
    const entries = await fs.readdir(p, { withFileTypes: true });
    for (const e of entries) {
      if (e.name === '__pycache__' || e.name === '.ipynb_checkpoints') continue;
      const fp = join(p, e.name);
      if (e.isDirectory()) {
        stat.dirs += 1;
        await walk(fp);
        continue;
      }
      stat.files += 1;
      const name = e.name.toLowerCase();
      const ext = name.slice(name.lastIndexOf('.'));

      if (e.name === DOC_NAME) {
        // Count README.rst lines (only at top level — the README directly in the leaf folder
        // is the canonical doc; sub-READMEs are visualization-specific)
        if (p === absPath) {
          try {
            const text = await fs.readFile(fp, 'utf8');
            stat.readmeLines = text.split('\n').length;
          } catch {
            /* ignore */
          }
        }
      } else if (SCRIPT_EXTS.has(ext)) {
        stat.scripts += 1;
      } else if (ASSET_EXTS.has(ext)) {
        stat.assets += 1;
      }
    }
  }

  await walk(absPath);

  const tier =
    stat.readmeLines >= COMPLETE_README_LINES &&
    stat.scripts >= COMPLETE_MIN_SCRIPTS &&
    stat.assets >= COMPLETE_MIN_ASSETS
      ? 'complete'
      : stat.readmeLines > 0 || stat.scripts > 0 || stat.assets > 0
      ? 'partial'
      : 'stub';

  return { tier, ...stat };
}

// ---------------------------------------------------------------
// 4. Main
// ---------------------------------------------------------------
async function main() {
  console.log(`v2 root:        ${V2_ROOT}`);
  console.log(`v1 root:        ${V1_ROOT}`);
  console.log(`subtopics.ts:   ${SUBTOPICS_PATH}`);
  console.log(`v1 content:     ${V1_CONTENT}`);
  console.log(`output JSON:    ${OUTPUT_PATH}\n`);

  // Make sure v1 exists.
  try {
    await fs.access(V1_CONTENT);
  } catch {
    console.error(`v1 content directory not found at ${V1_CONTENT}`);
    console.error(`Set V1_ROOT env var to override, e.g. V1_ROOT=C:\\path\\to\\numpy-to-genAI`);
    process.exit(1);
  }

  const subtopics = await parseSubtopics();
  const mods = await parseModules();
  const v1Folders = await indexV1Folders();

  const totalLeavesInCatalog = Object.values(subtopics).reduce(
    (sum, subs) => sum + subs.reduce((s, sub) => s + sub.leaves.length, 0),
    0
  );
  console.log(
    `Parsed: ${totalLeavesInCatalog} leaves across ${Object.keys(subtopics).length} modules in subtopics.ts`
  );
  console.log(`Indexed: ${v1Folders.size} leaf folders found in v1\n`);

  // Build the inventory entry list.
  const entries = [];
  const stats = { complete: 0, partial: 0, stub: 0, missing: 0 };

  for (const modIdx of Object.keys(subtopics).sort()) {
    const mod = mods[modIdx] || {};
    for (const sub of subtopics[modIdx]) {
      for (const leaf of sub.leaves) {
        const v1Path = v1Folders.get(leaf.id) || null;
        let tier, scan;
        if (!v1Path) {
          tier = 'missing';
          scan = { readmeLines: 0, scripts: 0, assets: 0, dirs: 0, files: 0 };
        } else {
          scan = await classifyLeafFolder(v1Path);
          tier = scan.tier;
          delete scan.tier;
        }
        stats[tier] = (stats[tier] || 0) + 1;
        entries.push({
          leafId: leaf.id,
          leafTitle: leaf.title,
          lessonSlug: leaf.lessonSlug,
          subtopicId: sub.id,
          subtopicTitle: sub.title,
          moduleIdx: modIdx,
          moduleTitle: mod.title || null,
          moduleEm: mod.em || null,
          framework: mod.fw || null,
          cycle: mod.cycle || null,
          v1Path: v1Path ? v1Path.replace(/\\/g, '/') : null,
          v1PathRelative: v1Path
            ? v1Path.replace(V1_ROOT, '').replace(/^[\\/]/, '').replace(/\\/g, '/')
            : null,
          tier,
          readmeLines: scan.readmeLines,
          scripts: scan.scripts,
          assets: scan.assets,
          totalDirs: scan.dirs,
          totalFiles: scan.files,
          // Boolean: does v2 already ship this lesson?
          shippedInV2: !!leaf.lessonSlug,
        });
      }
    }
  }

  // Per-module breakdown.
  const perModule = {};
  for (const e of entries) {
    perModule[e.moduleIdx] = perModule[e.moduleIdx] || {
      moduleIdx: e.moduleIdx,
      moduleTitle: e.moduleTitle,
      framework: e.framework,
      cycle: e.cycle,
      leaves: 0,
      complete: 0,
      partial: 0,
      stub: 0,
      missing: 0,
      shipped: 0,
    };
    perModule[e.moduleIdx].leaves += 1;
    perModule[e.moduleIdx][e.tier] += 1;
    if (e.shippedInV2) perModule[e.moduleIdx].shipped += 1;
  }

  const inventory = {
    generatedAt: new Date().toISOString(),
    v1Root: V1_ROOT.replace(/\\/g, '/'),
    v2Root: V2_ROOT.replace(/\\/g, '/'),
    totals: {
      catalogLeaves: totalLeavesInCatalog,
      v1Folders: v1Folders.size,
      ...stats,
      shippedInV2: entries.filter((e) => e.shippedInV2).length,
    },
    perModule,
    entries,
  };

  await fs.mkdir(dirname(OUTPUT_PATH), { recursive: true });
  await fs.writeFile(OUTPUT_PATH, JSON.stringify(inventory, null, 2) + '\n', 'utf8');

  // Console summary.
  console.log('=== Inventory summary ===');
  console.log(`  complete: ${stats.complete}`);
  console.log(`  partial:  ${stats.partial}`);
  console.log(`  stub:     ${stats.stub}`);
  console.log(`  missing:  ${stats.missing}`);
  console.log(`  shipped:  ${inventory.totals.shippedInV2}`);
  console.log('');
  console.log('Per module:');
  console.log('  M  | leaves | complete | partial | stub | missing | shipped');
  console.log('  ---+--------+----------+---------+------+---------+--------');
  for (const idx of Object.keys(perModule).sort()) {
    const r = perModule[idx];
    console.log(
      `  ${idx} |   ${String(r.leaves).padStart(3)}  |    ${String(r.complete).padStart(3)}   |   ${String(
        r.partial
      ).padStart(3)}   |  ${String(r.stub).padStart(3)} |   ${String(r.missing).padStart(3)}   |   ${String(r.shipped).padStart(3)}`
    );
  }
  console.log(`\nInventory written to ${OUTPUT_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
