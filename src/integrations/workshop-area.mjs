/**
 * Workshop participant area: build flag, routes and a post-build leak check
 * (workshop-planning/05 §7, S1 and S3).
 *
 * Lives under src/ (tracked) rather than scripts/ (local only), so the leak
 * check runs inside every `astro build`, on Netlify too.
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEnv } from 'vite';

// Opt-in flags: only the exact value "true" turns them on; unset or anything
// else leaves dist/ exactly as it was. This is the opposite of
// PUBLIC_PYTHON_RUNNER, which is on unless set to "false". loadEnv reads .env
// files as well as the process environment (Netlify).
const env = loadEnv(process.env.NODE_ENV ?? 'production', process.cwd(), 'PUBLIC_');
const flag = (name) => (process.env[name] ?? env[name]) === 'true';

/** The gated participant area (/workshops/w1-see, …). */
export const WORKSHOP_AREA = flag('PUBLIC_WORKSHOP_AREA');

/** The six-workshop series section on the public /workshops page (BLD-09). */
export const WORKSHOP_SERIES = flag('PUBLIC_WORKSHOP_SERIES');

/** Public pages below /workshops (the ticket terms); every other path below it is the participant area. */
const PUBLIC_WORKSHOP_PAGES = ['/workshops/terms'];

/** Paths below /workshops are the participant area; /workshops itself and PUBLIC_WORKSHOP_PAGES are public. */
export const isWorkshopAreaPath = (pathname) =>
  /^\/workshops\/[^/]/.test(pathname) && !PUBLIC_WORKSHOP_PAGES.includes(pathname.replace(/(\.html|\/)$/, ''));

const SITE = 'https://pixels2genai.art';
// "/workshops/" followed by anything but a delimiter, inside text files (the public terms page excepted).
const AREA_PATH_IN_TEXT = /\/workshops\/(?!terms\b)[^\s/)"'<>]/;

// Things that must never reach the built site, in any file. A match fails the
// build: a key or dev address that slipped into browser code is a leak even if
// no page links to it. (Real secrets live only in Cloud Run Secret Manager and
// Netlify environment variables, never under a PUBLIC_ name.)
const SECRET_PATTERNS = [
  { name: 'Anthropic API key', re: /sk-ant-[A-Za-z0-9_-]{8,}/ },
  { name: 'OpenAI-style API key', re: /\bsk-(?:proj-)?[A-Za-z0-9]{32,}/ },
  { name: 'Google API key', re: /AIza[0-9A-Za-z_-]{35}/ },
  { name: 'private key', re: /-----BEGIN [A-Z ]*PRIVATE KEY-----/ },
  { name: 'tutor dev token', re: /TUTOR_DEV_TOKEN|dev-local/ },
  { name: 'secret or pepper assignment', re: /\b[A-Z0-9_]*(?:SECRET|PEPPER)[A-Z0-9_]*["']?\s*[:=]\s*["'][^"']{6,}/ },
  { name: 'localhost address', re: /\b(?:localhost|127\.0\.0\.1):\d{2,5}/ },
];
// Workshop lesson material must never reach the public site before the release (DEC-26, DEC-77): the
// lesson sources, their media (cells, solutions) and the answer checks. A match fails the build.
const LESSON_MATERIAL = [
  { name: 'workshop media folder', re: /(^|\/)workshop-media\//i },
  { name: 'workshop-area source folder', re: /(^|\/)workshop-area\//i },
  { name: 'answer-check file', re: /\.check\.py$/i },
  { name: 'workshop lesson page', re: /(^|\/)workshops\/w[1-7]-[a-z]+\/[0-9]/i },
];
// SEC-32: with the area flag off, no built text file may even point at the workshop media route, so a page
// or script that links or fetches /workshop-media/... fails the build too, not only a copied file.
const LESSON_MEDIA_IN_TEXT = /\/workshop-media\//i;
// Private working folders and files (CLAUDE.local.md "private, never in the public repo"). They must never
// be in dist/, whatever the flags, so a stray copy into public/ fails the build.
const PRIVATE_PATHS = [
  { name: 'workshop planning folder', re: /(^|\/)workshop-planning\//i },
  { name: 'AI tutor planning folder', re: /(^|\/)ai-tutor(-planning)?\//i },
  { name: 'tutor component folder', re: /(^|\/)components\/tutor\//i },
  { name: 'Claude settings folder', re: /(^|\/)\.claude\//i },
  { name: 'local working-rules file', re: /(^|\/)CLAUDE\.local\.md$/i },
  { name: 'environment file', re: /(^|\/)\.env(\.[^/]*)?$/i },
];
// Includes the downloadable lesson scripts (.py) and notebooks.
const TEXT_FILE = /\.(html|js|mjs|css|json|txt|xml|webmanifest|svg|map|py|ipynb|md)$/i;

// Area pages: no analytics (until the privacy review), and nothing a strict
// Content-Security-Policy would have to allow with 'unsafe-inline' or
// 'unsafe-hashes' (inline event handlers, javascript: URLs). SEC-15.
const AREA_FORBIDDEN = [
  { name: 'analytics script', re: /cloud\.umami\.is|umami\.track/ },
  { name: 'inline event handler', re: /<[a-z][^>]*\son[a-z]+\s*=/i },
  { name: 'javascript: URL', re: /(?:href|src|action)\s*=\s*["']?\s*javascript:/i },
];

/** Every file under dir, recursively. */
function filesUnder(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...filesUnder(p));
    else out.push(p);
  }
  return out;
}

/**
 * Fails the build when:
 *   - a path below /workshops is in a sitemap, llms.txt or feed.xml;
 *   - the public /workshops page is missing from the sitemap;
 *   - the area flag is off but area pages were built anyway;
 *   - the area flag is on and an area page lacks noindex, carries JSON-LD,
 *     loads analytics, or has inline event handlers / javascript: URLs;
 *   - the area flag is off and workshop lesson material was built (LESSON_MATERIAL), or a text file
 *     points at /workshop-media/ (LESSON_MEDIA_IN_TEXT, SEC-32);
 *   - a private working folder or file reached dist/ (PRIVATE_PATHS), whatever the flags;
 *   - any text file in dist/ contains a secret pattern (SECRET_PATTERNS).
 */
function checkForLeaks(distDir, logger) {
  const errors = [];

  const sitemaps = fs.readdirSync(distDir).filter((f) => /^sitemap-\d+\.xml$/.test(f));
  if (sitemaps.length === 0) errors.push('No sitemap-*.xml in dist/.');
  const locs = sitemaps.flatMap((f) =>
    [...fs.readFileSync(path.join(distDir, f), 'utf8').matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]),
  );
  for (const loc of locs) {
    if (isWorkshopAreaPath(new URL(loc).pathname)) errors.push(`Participant-area path in the sitemap: ${loc}`);
  }
  if (!locs.includes(`${SITE}/workshops`)) errors.push(`The public page ${SITE}/workshops is missing from the sitemap.`);

  for (const file of ['llms.txt', 'feed.xml']) {
    const full = path.join(distDir, file);
    if (!fs.existsSync(full)) {
      errors.push(`dist/${file} is missing.`);
      continue;
    }
    for (const line of fs.readFileSync(full, 'utf8').split('\n')) {
      if (AREA_PATH_IN_TEXT.test(line)) errors.push(`Participant-area path in ${file}: ${line.trim().slice(0, 120)}`);
    }
  }

  // dist/workshops/ also holds the pilot's poster and gallery images, which
  // are public assets; only .html pages count, and the public terms page doesn't.
  const areaPages = [];
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(p);
      else if (entry.name.endsWith('.html') && isWorkshopAreaPath('/' + path.relative(distDir, p).replace(/\\/g, '/'))) areaPages.push(p);
    }
  };
  walk(path.join(distDir, 'workshops'));

  for (const page of areaPages) {
    const rel = path.relative(distDir, page).replace(/\\/g, '/');
    if (!WORKSHOP_AREA) {
      errors.push(`PUBLIC_WORKSHOP_AREA is off, but ${rel} was built.`);
      continue;
    }
    const html = fs.readFileSync(page, 'utf8');
    if (!/<meta name="robots" content="noindex"/.test(html)) errors.push(`${rel} has no robots noindex meta.`);
    if (html.includes('application/ld+json')) errors.push(`${rel} carries JSON-LD.`);
    for (const rule of AREA_FORBIDDEN) {
      if (rule.re.test(html)) errors.push(`${rel} contains a forbidden ${rule.name}.`);
    }
  }

  // The live Run buttons (python-worker.mjs) and the workshop code cells
  // (cell-worker.mjs) must load the same Pyodide build: one Python for the site.
  const pinned = (name) => {
    const full = path.join(distDir, 'runner', name);
    if (!fs.existsSync(full)) return null;
    return (fs.readFileSync(full, 'utf8').match(/PYODIDE_VERSION = "([\d.]+)"/) ?? [])[1] ?? 'unreadable';
  };
  const liveVersion = pinned('python-worker.mjs');
  const cellVersion = pinned('cell-worker.mjs');
  if (liveVersion && cellVersion && liveVersion !== cellVersion) {
    errors.push(`Pyodide versions differ: python-worker.mjs pins ${liveVersion}, cell-worker.mjs pins ${cellVersion}.`);
  }

  let scanned = 0;
  for (const file of filesUnder(distDir)) {
    const rel = path.relative(distDir, file).replace(/\\/g, '/');
    // The tutor panel lives in the gitignored src/components/tutor/ until the tutor launches, but a local
    // production build still bundles it when that folder exists. Build anything you upload from a clean export.
    if (/TutorPanel|TutorDev/.test(rel)) errors.push(`Tutor panel code was built: ${rel} (build from a clean export).`);
    if (!WORKSHOP_AREA) {
      for (const rule of LESSON_MATERIAL) {
        if (rule.re.test(rel)) errors.push(`PUBLIC_WORKSHOP_AREA is off, but a ${rule.name} was built: ${rel}`);
      }
    }
    for (const rule of PRIVATE_PATHS) {
      if (rule.re.test(rel)) errors.push(`A private ${rule.name} reached dist/: ${rel}`);
    }
    if (!TEXT_FILE.test(file)) continue;
    scanned += 1;
    const text = fs.readFileSync(file, 'utf8');
    if (!WORKSHOP_AREA && LESSON_MEDIA_IN_TEXT.test(text)) {
      errors.push(`PUBLIC_WORKSHOP_AREA is off, but ${rel} points at /workshop-media/.`);
    }
    for (const rule of SECRET_PATTERNS) {
      const match = text.match(rule.re);
      // Report where, never the matched value itself (the log may be public).
      if (match) errors.push(`Possible ${rule.name} in ${path.relative(distDir, file).replace(/\\/g, '/')}.`);
    }
  }

  if (errors.length) {
    for (const e of errors) logger.error(e);
    throw new Error(`Workshop-area leak check failed with ${errors.length} error(s).`);
  }
  logger.info(
    `Leak check OK: area ${WORKSHOP_AREA ? 'on' : 'off'}, ${areaPages.length} area page(s), ${locs.length} sitemap URL(s), ${scanned} file(s) scanned for secrets.`,
  );
}

/**
 * Pages under src/pages are always built, so the area's pages live in
 * src/workshop-area/pages and are routed here only when the flag is on. With
 * the flag off the routes don't exist at all: nothing to leak, nothing to gate.
 * List this integration after @astrojs/sitemap so the sitemap exists when the
 * check runs.
 */
export default function workshopArea() {
  return {
    name: 'p2g-workshop-area',
    hooks: {
      'astro:config:setup': ({ injectRoute, updateConfig }) => {
        // Astro bundles a component's CSS even behind a runtime condition, so
        // the /workshops parts are chosen here: the branded ones
        // (components/workshops/brand/) or today's markup verbatim (classic/),
        // which keeps /workshops byte-identical while the flag is off. Pages
        // import them as 'p2g:workshop-brand/Hero.astro' and so on.
        const brandDir = WORKSHOP_SERIES ? 'brand' : 'classic';
        updateConfig({
          vite: {
            resolve: {
              alias: [
                {
                  find: 'p2g:workshop-brand',
                  replacement: fileURLToPath(new URL(`../components/workshops/${brandDir}`, import.meta.url)),
                },
              ],
            },
          },
        });

        if (!WORKSHOP_AREA) return;
        injectRoute({
          pattern: '/workshops/[workshop]',
          entrypoint: './src/workshop-area/pages/arc.astro',
        });
        injectRoute({
          pattern: '/workshops/my',
          entrypoint: './src/workshop-area/pages/my.astro',
        });
        injectRoute({
          pattern: '/workshops/[workshop]/[lesson]',
          entrypoint: './src/workshop-area/pages/lesson.astro',
        });
      },
      'astro:build:done': ({ dir, logger }) => checkForLeaks(fileURLToPath(dir), logger),
    },
  };
}
