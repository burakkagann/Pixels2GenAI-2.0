/**
 * One-shot: prepare the March 2026 exhibition's new media for the web.
 *
 *  - Downsizes the raw 2-8 MB print PNGs (Maris Nieuwenhuis + Orbit Sediment)
 *    to ~2000px web JPGs under 500 KB (docs/references/visual-guidelines.md).
 *  - Converts the two video still frames into autoplay-video posters.
 *  - Copies the two installation recordings from the burakkagan.dev repo into
 *    this repo's public/ tree (referenced locally, never hot-linked).
 *  - Removes each raw source only after its derivative is written.
 *
 * Idempotent: re-running re-encodes from any raw source still present and
 * skips conversions whose source has already been consumed.
 *
 * Run from repo root:  node scripts/migration/optimize-exhibition-assets.mjs
 */
import sharp from 'sharp';
import { existsSync, statSync, copyFileSync, unlinkSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const PRINTS = 'public/exhibitions/prints';
const ANIM = 'public/exhibitions/animated';
const MAX_BYTES = 500 * 1024;

// Source recordings live in the sibling portfolio repo.
const DEV_REPO = 'C:/Users/aslih/OneDrive/Masaüstü/git-repos/burakkagan.dev/public/projects';

/** Encode `src` to a JPEG <= MAX_BYTES, stepping quality then dimensions. */
async function toWebJpg(src, dest, maxEdge) {
  let quality = 84;
  let edge = maxEdge;
  for (let i = 0; i < 10; i++) {
    const buf = await sharp(src)
      .resize({ width: edge, height: edge, fit: 'inside', withoutEnlargement: true })
      .jpeg({ quality, mozjpeg: true, chromaSubsampling: '4:2:0' })
      .toBuffer();
    const last = quality <= 64 && edge <= maxEdge * 0.7;
    if (buf.length <= MAX_BYTES || last) {
      writeFileSync(dest, buf);
      return { bytes: buf.length, quality, edge };
    }
    if (quality > 68) quality -= 6;
    else edge = Math.round(edge * 0.92);
  }
}

// [rawSourcePNG, destJPG, maxEdge]
const PRINT_JOBS = [
  [`${PRINTS}/print_frame2_spark.png`,        `${PRINTS}/array-zero-02-spark.jpg`,        2000],
  [`${PRINTS}/print_frame4_bloom_spiral.png`, `${PRINTS}/array-zero-04-spiral-bloom.jpg`, 2000],
  [`${PRINTS}/thresholds_tanh_tectonic_interference_geological.png`, `${PRINTS}/tectonic-threshold-tanh.jpg`, 2000],
  [`${PRINTS}/Maris - (1)MengerFlake_2880x2880.png`, `${PRINTS}/maris-menger-flake.jpg`, 2000],
  [`${PRINTS}/Maris - (2)Koch3D_2880x1920.png`,      `${PRINTS}/maris-koch-3d.jpg`,       2000],
  [`${PRINTS}/Maris - (3)a05sceneRework_2880x1920.png`, `${PRINTS}/maris-scene-rework.jpg`, 2000],
  [`${PRINTS}/variant_f_trichrome.png`,  `${PRINTS}/orbit-sediment-trichrome.jpg`,  2000],
  [`${PRINTS}/variant_g_widespread.png`, `${PRINTS}/orbit-sediment-widespread.jpg`, 2000],
  [`${PRINTS}/variant_h_dualglow.png`,   `${PRINTS}/orbit-sediment-dualglow.jpg`,   2000],
];

const POSTER_JOBS = [
  [`${PRINTS}/metabolic-rate-still-frame.png`,    `${ANIM}/neural-mycelium-poster.jpg`,    1600],
  [`${PRINTS}/selecton-pressure-still-frame.png`, `${ANIM}/selection-pressure-poster.jpg`, 1600],
];

const VIDEO_JOBS = [
  [`${DEV_REPO}/mycelium-metabolic-rate.mp4`, `${ANIM}/neural-mycelium.mp4`],
  [`${DEV_REPO}/selection-pressure.mp4`,      `${ANIM}/selection-pressure.mp4`],
];

const kb = (b) => (b / 1024).toFixed(0) + ' KB';

for (const [src, dest, maxEdge] of [...PRINT_JOBS, ...POSTER_JOBS]) {
  if (!existsSync(src)) {
    console.log(existsSync(dest) ? `skip   ${dest}  (already built)` : `MISS   ${src}`);
    continue;
  }
  const r = await toWebJpg(resolve(src), resolve(dest), maxEdge);
  const flag = r.bytes <= MAX_BYTES ? 'ok ' : 'WARN';
  console.log(`${flag}    ${dest}  ${kb(r.bytes)}  q${r.quality} @${r.edge}px  (from ${kb(statSync(src).size)})`);
  unlinkSync(src);
}

for (const [src, dest] of VIDEO_JOBS) {
  if (existsSync(dest)) { console.log(`skip   ${dest}  (already copied)`); continue; }
  if (!existsSync(src)) { console.log(`MISS   ${src}`); continue; }
  copyFileSync(resolve(src), resolve(dest));
  console.log(`copy   ${dest}  ${kb(statSync(dest).size)}`);
}

// Drop the work that was never part of the show.
const carpet = `${PRINTS}/fractal-square-carpet.jpg`;
if (existsSync(carpet)) { unlinkSync(carpet); console.log(`rm     ${carpet}`); }

console.log('done.');
