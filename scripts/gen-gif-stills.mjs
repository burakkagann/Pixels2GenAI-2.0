#!/usr/bin/env node
/**
 * Generate a still frame for every animated GIF under public/lesson-media/.
 *
 * <Figure> serves `<name>.still.png` instead of `<name>.gif` to visitors who
 * have "reduce motion" turned on (a <picture> media query, no JavaScript), so
 * looping lesson animations never play for them (WCAG 2.2.2 Pause, Stop,
 * Hide). The LAST frame is used because most lesson GIFs build an image up
 * step by step: the first frame is often blank, the last shows the result.
 *
 * Idempotent: existing stills are kept unless --force is passed. Run after
 * adding or replacing a GIF (the lesson-port workflow), then commit the PNGs.
 *
 *   node scripts/gen-gif-stills.mjs            # new GIFs only
 *   node scripts/gen-gif-stills.mjs --force    # regenerate all
 */
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const ROOT = path.join(process.cwd(), 'public', 'lesson-media');
const FORCE = process.argv.includes('--force');

const walk = (dir) =>
  fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const p = path.join(dir, e.name);
    return e.isDirectory() ? walk(p) : e.name.toLowerCase().endsWith('.gif') ? [p] : [];
  });

let made = 0, kept = 0, still = 0;
for (const gif of walk(ROOT)) {
  const out = gif.replace(/\.gif$/i, '.still.png');
  if (!FORCE && fs.existsSync(out)) { kept++; continue; }
  const { pages = 1 } = await sharp(gif).metadata();
  if (pages < 2) { still++; continue; } // not animated: nothing to replace
  await sharp(gif, { page: pages - 1 }).png({ compressionLevel: 9, palette: true, quality: 90 }).toFile(out);
  made++;
  console.log(`${path.relative(ROOT, out)}  (${pages} frames, ${Math.round(fs.statSync(out).size / 1024)} KB)`);
}
console.log(`\n${made} still(s) written, ${kept} already present, ${still} GIF(s) not animated.`);
