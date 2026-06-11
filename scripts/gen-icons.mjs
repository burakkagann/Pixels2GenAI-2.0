/**
 * Rasterize public/favicon.svg into the binary icon set referenced by
 * Base.astro and site.webmanifest:
 *
 *   favicon.ico          16/32/48 multi-res, transparent background
 *   apple-touch-icon.png 180×180, solid brand background (iOS adds corners)
 *   icon-192.png         192×192, solid background (manifest / Android)
 *   icon-512.png         512×512, solid background (manifest / maskable)
 *
 * Idempotent: re-run after editing favicon.svg. Requires devDeps sharp +
 * png-to-ico. Run via `npm run gen-icons`.
 */
import sharp from 'sharp';
import pngToIco from 'png-to-ico';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const pub = join(root, 'public');
const svg = await readFile(join(pub, 'favicon.svg'));

// --bg-deep from src/styles/tokens.css — matches the dark-default page bg.
const BG = { r: 0x11, g: 0x0d, b: 0x16, alpha: 1 };
const TRANSPARENT = { r: 0, g: 0, b: 0, alpha: 0 };

// Render the SVG art at `inner` px (with breathing room) centered on a
// `size`×`size` solid-background square.
async function solid(size, pad = 0.16) {
  const inner = Math.round(size * (1 - pad * 2));
  const art = await sharp(svg, { density: 512 })
    .resize(inner, inner, { fit: 'contain', background: TRANSPARENT })
    .png()
    .toBuffer();
  return sharp({ create: { width: size, height: size, channels: 4, background: BG } })
    .composite([{ input: art, gravity: 'center' }])
    .png()
    .toBuffer();
}

async function transparent(size) {
  return sharp(svg, { density: 512 })
    .resize(size, size, { fit: 'contain', background: TRANSPARENT })
    .png()
    .toBuffer();
}

await writeFile(join(pub, 'apple-touch-icon.png'), await solid(180));
await writeFile(join(pub, 'icon-192.png'), await solid(192));
await writeFile(join(pub, 'icon-512.png'), await solid(512));

const ico = await pngToIco([await transparent(16), await transparent(32), await transparent(48)]);
await writeFile(join(pub, 'favicon.ico'), ico);

console.log('Generated favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png');
