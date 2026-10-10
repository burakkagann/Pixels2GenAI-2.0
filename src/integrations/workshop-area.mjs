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

/** Paths below /workshops are the participant area; /workshops itself is public. */
export const isWorkshopAreaPath = (pathname) => /^\/workshops\/[^/]/.test(pathname);

const SITE = 'https://pixels2genai.art';
// "/workshops/" followed by anything but a delimiter, inside text files.
const AREA_PATH_IN_TEXT = /\/workshops\/[^\s/)"'<>]/;

/**
 * Fails the build when:
 *   - a path below /workshops is in a sitemap, llms.txt or feed.xml;
 *   - the public /workshops page is missing from the sitemap;
 *   - the area flag is off but area pages were built anyway;
 *   - the area flag is on and an area page lacks noindex or carries JSON-LD.
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
  // are public assets; only .html pages count.
  const areaPages = [];
  const walk = (dir) => {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(p);
      else if (entry.name.endsWith('.html')) areaPages.push(p);
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
  }

  if (errors.length) {
    for (const e of errors) logger.error(e);
    throw new Error(`Workshop-area leak check failed with ${errors.length} error(s).`);
  }
  logger.info(
    `Leak check OK: area ${WORKSHOP_AREA ? 'on' : 'off'}, ${areaPages.length} area page(s), ${locs.length} sitemap URL(s).`,
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
      'astro:config:setup': ({ injectRoute }) => {
        if (!WORKSHOP_AREA) return;
        injectRoute({
          pattern: '/workshops/[workshop]',
          entrypoint: './src/workshop-area/pages/arc.astro',
        });
      },
      'astro:build:done': ({ dir, logger }) => checkForLeaks(fileURLToPath(dir), logger),
    },
  };
}
