#!/usr/bin/env node
/**
 * Generate the Open Graph background image: a striking exhibition print,
 * cropped to 1200x630 and darkened with a gradient scrim so overlaid title
 * text stays readable. Output is consumed as `bgImage` by src/pages/og/[...route].ts.
 *
 * One-shot generator (commit the output). Re-run with `npm run gen-og-bg` if the
 * source print or scrim changes.
 */
import sharp from 'sharp';
import { mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';

const SRC = 'public/exhibitions/prints/orbit-sediment-dualglow.jpg';
const OUT = 'src/assets/og-bg.jpg';
const W = 1200;
const H = 630;

// Scrim: an overall mute, plus darker gradients on the left and bottom (where
// the title/description sit) so the print's glow stays visible on the right.
const scrim = Buffer.from(
  `<svg width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">
     <defs>
       <linearGradient id="lr" x1="0" y1="0" x2="1" y2="0">
         <stop offset="0" stop-color="#000" stop-opacity="0.72"/>
         <stop offset="0.55" stop-color="#000" stop-opacity="0.12"/>
         <stop offset="1" stop-color="#000" stop-opacity="0.30"/>
       </linearGradient>
       <linearGradient id="bt" x1="0" y1="1" x2="0" y2="0">
         <stop offset="0" stop-color="#000" stop-opacity="0.58"/>
         <stop offset="0.45" stop-color="#000" stop-opacity="0.06"/>
         <stop offset="1" stop-color="#000" stop-opacity="0"/>
       </linearGradient>
     </defs>
     <rect width="${W}" height="${H}" fill="#0c0913" fill-opacity="0.26"/>
     <rect width="${W}" height="${H}" fill="url(#lr)"/>
     <rect width="${W}" height="${H}" fill="url(#bt)"/>
   </svg>`,
);

await mkdir(dirname(OUT), { recursive: true });
await sharp(SRC)
  .resize(W, H, { fit: 'cover', position: 'centre' })
  .composite([{ input: scrim, top: 0, left: 0 }])
  .jpeg({ quality: 88, mozjpeg: true })
  .toFile(OUT);

console.log(`Wrote ${OUT} (${W}x${H}) from ${SRC}`);