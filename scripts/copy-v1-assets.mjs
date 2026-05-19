// ============================================================
//  copy-v1-assets.mjs
//  One-shot migration of lesson assets (PNG / GIF / .py / .pth)
//  from the v1 numpy-to-genAI tree into v2's public/lessons/.
//
//  Run with: npm run copy-assets
//
//  v1 is treated as read-only: this script only reads from it.
//  Idempotent: re-running overwrites destination files.
// ============================================================

import { promises as fs } from 'node:fs';
import { dirname, join, basename, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const V2_ROOT = resolve(__dirname, '..');
const V1_ROOT = resolve(V2_ROOT, '..'); // parent: numpy-to-genAI/

const LESSONS = [
  {
    slug: '1.1.1',
    src: 'content/Module_01_pixel_fundamentals/1.1_grayscale_color_basics/1.1.1_color_basics/rgb',
    excludes: [],
  },
  {
    slug: '4.1.1',
    src: 'content/Module_04_fractals_recursion/4.1_classical_fractals/4.1.1_fractal_square/fractal_square',
    excludes: [],
  },
  {
    slug: '12.1.2',
    src: 'content/Module_12_generative_ai_models/12.1_generative_adversarial_networks/12.1.2_dcgan_art',
    // The two fabric folders are 22MB of training data that lesson visitors
    // don't need to view the page. Linked from the lesson as a separate
    // download instead. __pycache__ is build noise.
    excludes: ['__pycache__', 'african_fabric_dataset', 'african_fabric_processed'],
  },
];

// File extensions worth copying. README.rst is intentionally NOT included —
// the MDX hand-port is the canonical source in v2.
const KEEP_EXT = new Set(['.png', '.gif', '.jpg', '.jpeg', '.svg', '.py', '.pth', '.txt']);

async function copyLessonAssets({ slug, src, excludes }) {
  const absSrc = join(V1_ROOT, src);
  const absDst = join(V2_ROOT, 'public', 'lessons', slug);

  let stat;
  try {
    stat = await fs.stat(absSrc);
  } catch {
    console.error(`  [skip] source missing: ${absSrc}`);
    return { slug, copied: 0, skipped: 0 };
  }
  if (!stat.isDirectory()) {
    console.error(`  [skip] source is not a directory: ${absSrc}`);
    return { slug, copied: 0, skipped: 0 };
  }

  await fs.mkdir(absDst, { recursive: true });

  const entries = await fs.readdir(absSrc, { withFileTypes: true });
  let copied = 0;
  let skipped = 0;
  for (const entry of entries) {
    if (excludes.includes(entry.name)) {
      skipped++;
      continue;
    }
    if (entry.isDirectory()) {
      skipped++;
      continue;
    }
    const ext = entry.name.slice(entry.name.lastIndexOf('.')).toLowerCase();
    if (!KEEP_EXT.has(ext)) {
      skipped++;
      continue;
    }
    const srcPath = join(absSrc, entry.name);
    const dstPath = join(absDst, entry.name);
    await fs.copyFile(srcPath, dstPath);
    copied++;
  }
  return { slug, copied, skipped };
}

async function main() {
  console.log(`v1 root: ${V1_ROOT}`);
  console.log(`v2 root: ${V2_ROOT}\n`);

  const results = [];
  for (const lesson of LESSONS) {
    console.log(`→ ${lesson.slug}`);
    const r = await copyLessonAssets(lesson);
    console.log(`   ${r.copied} copied, ${r.skipped} skipped`);
    results.push(r);
  }

  const total = results.reduce((sum, r) => sum + r.copied, 0);
  console.log(`\nDone — ${total} files copied across ${LESSONS.length} lessons.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
