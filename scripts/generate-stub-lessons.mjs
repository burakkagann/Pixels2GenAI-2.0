// ============================================================
//  generate-stub-lessons.mjs
//  For every leaf in the v1 inventory:
//    1. If src/content/lessons/<slug>.mdx already exists AND does NOT
//       contain the {/* placeholder */} marker → SKIP (hand-written
//       lesson; never clobber).
//    2. Otherwise, write a stub MDX with full schema-valid frontmatter
//       and a "Coming soon" body.
//
//  Then:
//    3. Update src/data/subtopics.ts to add `lessonSlug: '<id>'` to
//       every leaf that doesn't have one.
//    4. Update src/data/modules.ts to set `firstLesson` for every
//       module that doesn't have one (using the first leaf in catalog
//       order).
//
//  Idempotent: re-running re-emits stubs (overwriting) but leaves
//  hand-written lessons untouched.
//
//  Usage:
//    node scripts/generate-stub-lessons.mjs
//    node scripts/generate-stub-lessons.mjs --dry-run
// ============================================================

import { promises as fs } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const V2_ROOT = resolve(__dirname, '..');
const INVENTORY_PATH = join(
  V2_ROOT,
  'thesis_automation',
  'reports',
  'migration-inventory.json'
);
const LESSONS_DIR = join(V2_ROOT, 'src', 'content', 'lessons');
const SUBTOPICS_PATH = join(V2_ROOT, 'src', 'data', 'subtopics.ts');
const MODULES_PATH = join(V2_ROOT, 'src', 'data', 'modules.ts');

const DRY_RUN = process.argv.includes('--dry-run');
const PLACEHOLDER_MARKER = '{/* placeholder */}';

// Module label, e.g. '01' → 'M 01'.
function moduleLabel(idx) {
  return `M ${idx}`;
}

// F-code → frontmatter framework value.
function frameworkSlug(fw) {
  return (
    {
      F1: 'hands-on',
      F2: 'conceptual',
      'F1+F2': 'hybrid',
      F3: 'project',
    }[fw] || 'hands-on'
  );
}

// Friendly framework label for the stub body.
function frameworkLabel(fw) {
  return (
    {
      F1: 'Hands-On Discovery',
      F2: 'Conceptual Deep-Dive',
      'F1+F2': 'Hands-On + Conceptual Hybrid',
      F3: 'Project-Based',
    }[fw] || fw
  );
}

// Default level by module range.
function defaultLevel(idx) {
  const n = parseInt(idx, 10);
  if (n <= 3) return 'beginner';
  if (n <= 6) return 'beginner-intermediate';
  if (n <= 9) return 'intermediate';
  if (n <= 11) return 'intermediate-advanced';
  return 'advanced';
}

// Cycle name for the body.
function cycleName(cycle) {
  return (
    {
      I: 'Foundations',
      II: 'Machine Learning',
      III: 'Generative AI',
    }[cycle] || cycle
  );
}

// ---------------------------------------------------------------
// Build a stub MDX file for one entry.
// ---------------------------------------------------------------
function renderStub(entry, prevEntry, nextEntry) {
  const slug = entry.leafId;
  const level = defaultLevel(entry.moduleIdx);
  const fw = frameworkSlug(entry.framework);
  const fwLabel = frameworkLabel(entry.framework);
  const cycle = entry.cycle;
  const cyName = cycleName(cycle);
  const modTitle = `${entry.moduleTitle}${
    entry.moduleEm ? ' ' + entry.moduleEm : ''
  }`.trim();

  const prevYaml = prevEntry
    ? `prev:\n  slug: "${prevEntry.leafId}"\n  title: "${escapeYaml(prevEntry.leafTitle)}"`
    : `prev: null`;
  const nextYaml = nextEntry
    ? `next:\n  slug: "${nextEntry.leafId}"\n  title: "${escapeYaml(nextEntry.leafTitle)}"`
    : `next: null`;

  const v1Note = entry.v1PathRelative
    ? `The v1 source for this exercise lives at \`${entry.v1PathRelative.replace(/\\/g, '/')}\` in the numpy-to-genAI repo.`
    : `No v1 source folder exists for this leaf yet. When authored, it should live under \`content/Module_${entry.moduleIdx}_*/${entry.subtopicId}_*/${slug}_*/\` in the numpy-to-genAI repo.`;

  return `---
module: "${moduleLabel(entry.moduleIdx)}"
cycle: "${cycle}"
title: "${escapeYaml(entry.leafTitle)}"
objective: "Coming soon — placeholder for the ${escapeYaml(entry.leafTitle)} lesson."
framework: "${fw}"
duration: "TBD"
level: "${level}"
${prevYaml}
${nextYaml}
backLink:
  href: "/#curriculum"
  label: "Back to Curriculum"
---

${PLACEHOLDER_MARKER}

## Coming soon <a id="coming-soon"></a>

This lesson is part of **Module ${entry.moduleIdx} — ${escapeMd(modTitle)}** in the *${cyName}* cycle (${fwLabel}). When written, it will cover **${escapeMd(entry.leafTitle)}**.

<Admonition type="note" title="Placeholder">
This lesson hasn't been written yet. ${v1Note}
</Admonition>

### What this lesson will cover

The full lesson will follow the standard ${fwLabel} format with **Execute → Modify → Create** scaffolding, runnable Python examples, generated outputs, and APA-cited references. Until then, this page is a structural placeholder so the curriculum navigation works end to end.

### Why this page exists

The Pixels2GenAI v2 site is being built from the ground up alongside the v1 reference platform (\`numpy-to-genAI\`). Every leaf in the curriculum tree gets a v2 page from day one so navigation, sibling-lesson links, and the curriculum map are complete even before each individual lesson is hand-ported. Placeholder pages like this one will be replaced by full lessons as they are written.
`;
}

function escapeYaml(s) {
  return String(s).replace(/"/g, '\\"');
}
function escapeMd(s) {
  return String(s).replace(/([*_`])/g, '\\$1');
}

// ---------------------------------------------------------------
// 1. Write stub MDX files (skipping hand-written ones).
// ---------------------------------------------------------------
async function generateStubs(entries) {
  await fs.mkdir(LESSONS_DIR, { recursive: true });

  let written = 0;
  let skippedExisting = 0;
  let skippedHandWritten = 0;

  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    const slug = entry.leafId;
    const path = join(LESSONS_DIR, `${slug}.mdx`);

    let isHandWritten = false;
    try {
      const existing = await fs.readFile(path, 'utf8');
      if (!existing.includes(PLACEHOLDER_MARKER)) {
        isHandWritten = true;
      }
    } catch {
      /* not present */
    }

    if (isHandWritten) {
      skippedHandWritten += 1;
      continue;
    }

    const prevEntry = i > 0 ? entries[i - 1] : null;
    const nextEntry = i < entries.length - 1 ? entries[i + 1] : null;
    const body = renderStub(entry, prevEntry, nextEntry);

    if (!DRY_RUN) {
      await fs.writeFile(path, body, 'utf8');
    }
    written += 1;
  }

  return { written, skippedExisting, skippedHandWritten };
}

// ---------------------------------------------------------------
// 2. Wire lessonSlug into subtopics.ts.
//    Each leaf entry in the file looks like:
//      { id: '1.1.1', title: 'Color Basics' },
//    or with existing lessonSlug:
//      { id: '1.1.1', title: 'Color Basics', lessonSlug: '1.1.1' },
//    We add lessonSlug: '<id>' when missing.
// ---------------------------------------------------------------
async function wireSubtopics() {
  const src = await fs.readFile(SUBTOPICS_PATH, 'utf8');
  // Match a leaf line: { id: 'X.Y.Z', title: '...' }   OR  { id: '...', title: '...', lessonSlug: '...' }
  // Capture: 1=id, 2=title, 3=existing lessonSlug or undefined
  const leafRe = /\{\s*id:\s*'([^']+)',\s*title:\s*'([^']+)'(?:,\s*lessonSlug:\s*'([^']+)')?\s*\}/g;

  let added = 0;
  let kept = 0;
  const out = src.replace(leafRe, (full, id, title, slug) => {
    if (slug) {
      kept += 1;
      return full;
    }
    added += 1;
    return `{ id: '${id}', title: '${title.replace(/'/g, "\\'")}', lessonSlug: '${id}' }`;
  });

  if (!DRY_RUN && out !== src) {
    await fs.writeFile(SUBTOPICS_PATH, out, 'utf8');
  }
  return { added, kept };
}

// ---------------------------------------------------------------
// 3. Wire firstLesson into modules.ts for modules that lack one.
// ---------------------------------------------------------------
async function wireModules(entries) {
  // Map module idx -> first leaf id (in catalog order).
  const firstLeafByModule = {};
  for (const e of entries) {
    if (!(e.moduleIdx in firstLeafByModule)) {
      firstLeafByModule[e.moduleIdx] = e.leafId;
    }
  }

  let src = await fs.readFile(MODULES_PATH, 'utf8');
  let added = 0;
  let kept = 0;

  // Each module: { idx: 'XX', title: '...', em: '...', fw: 'F?', cycle: '?'[, firstLesson: '...'][, capstone: true] }
  // We match per-line because the format is regular.
  const modRe =
    /(\{\s*idx:\s*'(\d{2})',\s*title:\s*'[^']+',\s*em:\s*'[^']*',\s*fw:\s*'[^']+',\s*cycle:\s*'[^']+')(\s*,\s*firstLesson:\s*'([^']+)')?(\s*,\s*capstone:\s*(?:true|false))?(\s*\})/g;

  src = src.replace(modRe, (full, head, idx, firstPart, existingFirst, capPart, tail) => {
    const firstLeaf = firstLeafByModule[idx];
    if (existingFirst) {
      kept += 1;
      return full;
    }
    if (!firstLeaf) {
      kept += 1;
      return full;
    }
    added += 1;
    // Insert firstLesson before the capstone segment (if any), or before the closing brace.
    return `${head}, firstLesson: '${firstLeaf}'${capPart || ''}${tail}`;
  });

  if (!DRY_RUN) {
    await fs.writeFile(MODULES_PATH, src, 'utf8');
  }
  return { added, kept };
}

// ---------------------------------------------------------------
async function main() {
  console.log(`v2 root:    ${V2_ROOT}`);
  console.log(`inventory:  ${INVENTORY_PATH}`);
  console.log(`dry-run:    ${DRY_RUN ? 'YES' : 'no'}\n`);

  const inventory = JSON.parse(await fs.readFile(INVENTORY_PATH, 'utf8'));
  const entries = inventory.entries;

  console.log(`Total leaves in inventory: ${entries.length}\n`);

  const r1 = await generateStubs(entries);
  console.log('Step 1 — stub MDX generation:');
  console.log(`  stubs written:      ${r1.written}`);
  console.log(`  hand-written kept:  ${r1.skippedHandWritten}\n`);

  const r2 = await wireSubtopics();
  console.log('Step 2 — wire subtopics.ts lessonSlug:');
  console.log(`  added:    ${r2.added}`);
  console.log(`  already had:  ${r2.kept}\n`);

  const r3 = await wireModules(entries);
  console.log('Step 3 — wire modules.ts firstLesson:');
  console.log(`  added:    ${r3.added}`);
  console.log(`  already had:  ${r3.kept}\n`);

  console.log(DRY_RUN ? '(dry-run, no files written)' : 'Done.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
