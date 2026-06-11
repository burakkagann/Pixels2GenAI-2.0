/**
 * Shared catalog reader for the lesson tooling.
 *
 * Parses the two TypeScript data files (src/data/curriculum/modules.ts and
 * src/data/curriculum/subtopics.ts) by extracting their exported literals and evaluating
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
  const src = fs.readFileSync(path.join(ROOT, 'src', 'data', 'curriculum', 'modules.ts'), 'utf8');
  return extractLiteral(src, 'MODULES');
}

/** Nested subtopics keyed by module idx. */
export function readSubtopics() {
  const src = fs.readFileSync(path.join(ROOT, 'src', 'data', 'curriculum', 'subtopics.ts'), 'utf8');
  return extractLiteral(src, 'SUBTOPICS');
}

/**
 * Walk src/content/lessons/ (Module_xx/x.y_subtopic/x.y.z_leaf.mdx — the
 * tree mirrors v1's content/ hierarchy) and map each lesson's numeric id
 * to its absolute file path. The id is the numeric prefix of the basename,
 * matching the glob loader's generateId in src/content/config.ts.
 */
function scanLessonFiles() {
  const bySlug = new Map();
  if (!fs.existsSync(LESSONS_DIR)) return bySlug;
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(p);
      else if (/\.mdx?$/.test(entry.name)) {
        const m = entry.name.match(/^(\d+(?:\.\d+)*)/);
        if (m) bySlug.set(m[1], p);
      }
    }
  };
  walk(LESSONS_DIR);
  return bySlug;
}

let lessonFileCache = null;
function lessonFiles() {
  if (!lessonFileCache) lessonFileCache = scanLessonFiles();
  return lessonFileCache;
}

/** Slugs of the MDX lessons that actually exist on disk. */
export function readLessonFiles() {
  return [...lessonFiles().keys()];
}

/** Absolute path to a lesson MDX file, or null. */
export function lessonFilePath(slug) {
  return lessonFiles().get(slug) ?? null;
}

/**
 * Asset locations for a lesson. The media tree mirrors the content tree:
 *   src/content/lessons/<module>/<subtopic>/<leaf>.mdx
 *   public/lesson-media/<module>/<subtopic>/<leaf>/
 * Returns { dir, url } or null when the lesson MDX doesn't exist.
 */
export function lessonAssetLocation(slug) {
  const file = lessonFilePath(slug);
  if (!file) return null;
  const rel = path
    .relative(LESSONS_DIR, file)
    .replace(/\\/g, '/')
    .replace(/\.mdx?$/, '');
  return {
    dir: path.join(PUBLIC_DIR, 'lesson-media', rel),
    url: `/lesson-media/${rel}/`,
  };
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
