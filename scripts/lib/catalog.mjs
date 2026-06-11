/**
 * Shared catalog reader for the lesson tooling.
 *
 * Parses the two TypeScript data files (src/data/modules.ts and
 * src/data/subtopics.ts) by extracting their exported literals and evaluating
 * them as plain JS. The literals are pure data (no type annotations inside the
 * values), so this is reliable without a TS toolchain.
 *
 * Also enumerates the shipped MDX lessons under src/content/lessons/.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, '..', '..');

const LESSONS_DIR = path.join(ROOT, 'src', 'content', 'lessons');
const PUBLIC_DIR = path.join(ROOT, 'public');

/**
 * Extract the object/array literal assigned to `export const <name>` and
 * evaluate it. Brace-matches with string awareness so values containing
 * braces or brackets don't confuse the scan.
 */
function extractLiteral(src, name) {
  const decl = `export const ${name}`;
  const start = src.indexOf(decl);
  if (start === -1) throw new Error(`Could not find "${decl}"`);
  let i = src.indexOf('=', start) + 1;
  while (/\s/.test(src[i])) i++;
  const open = src[i];
  const close = open === '{' ? '}' : ']';
  if (open !== '{' && open !== '[') {
    throw new Error(`Expected object/array literal for ${name}`);
  }
  let depth = 0;
  let inStr = false;
  let strCh = '';
  for (let j = i; j < src.length; j++) {
    const ch = src[j];
    if (inStr) {
      if (ch === '\\') { j++; continue; }
      if (ch === strCh) inStr = false;
      continue;
    }
    if (ch === "'" || ch === '"' || ch === '`') { inStr = true; strCh = ch; continue; }
    if (ch === open) depth++;
    else if (ch === close) {
      depth--;
      if (depth === 0) {
        const literal = src.slice(i, j + 1);
        // eslint-disable-next-line no-new-func
        return new Function(`return (${literal})`)();
      }
    }
  }
  throw new Error(`Unbalanced literal for ${name}`);
}

/** Flat module catalog (15 + capstone). */
export function readModules() {
  const src = fs.readFileSync(path.join(ROOT, 'src', 'data', 'modules.ts'), 'utf8');
  return extractLiteral(src, 'MODULES');
}

/** Nested subtopics keyed by module idx. */
export function readSubtopics() {
  const src = fs.readFileSync(path.join(ROOT, 'src', 'data', 'subtopics.ts'), 'utf8');
  return extractLiteral(src, 'SUBTOPICS');
}

/** Slugs of the MDX lessons that actually exist on disk. */
export function readLessonFiles() {
  if (!fs.existsSync(LESSONS_DIR)) return [];
  return fs
    .readdirSync(LESSONS_DIR)
    .filter((f) => f.endsWith('.mdx') || f.endsWith('.md'))
    .map((f) => f.replace(/\.mdx?$/, ''));
}

/** Absolute path to a lesson MDX file (mdx preferred). */
export function lessonFilePath(slug) {
  const mdx = path.join(LESSONS_DIR, `${slug}.mdx`);
  if (fs.existsSync(mdx)) return mdx;
  const md = path.join(LESSONS_DIR, `${slug}.md`);
  if (fs.existsSync(md)) return md;
  return null;
}

/** Resolve a site-absolute asset path ("/lessons/x/y.png") to a public/ path. */
export function publicAssetPath(sitePath) {
  const clean = sitePath.split(/[?#]/)[0];
  return path.join(PUBLIC_DIR, clean.replace(/^\//, ''));
}

/**
 * Build a per-module view: leaves, which are wired (have a lessonSlug), and
 * whether each wired slug has a matching MDX file. Returns an array preserving
 * MODULES order.
 */
export function buildModuleView() {
  const modules = readModules();
  const subtopics = readSubtopics();
  const files = new Set(readLessonFiles());

  return modules.map((m) => {
    const subs = subtopics[m.idx] ?? [];
    const leaves = subs.flatMap((s) =>
      s.leaves.map((l) => ({
        id: l.id,
        title: l.title,
        slug: l.lessonSlug ?? null,
        hasFile: l.lessonSlug ? files.has(l.lessonSlug) : false,
        subTitle: s.title,
      }))
    );
    const wired = leaves.filter((l) => l.slug);
    const shipped = wired.filter((l) => l.hasFile);
    return {
      idx: m.idx,
      title: `${m.title} ${m.em}`,
      fw: m.fw,
      cycle: m.cycle,
      firstLesson: m.firstLesson ?? null,
      subCount: subs.length,
      leaves,
      wired,
      shipped,
    };
  });
}
