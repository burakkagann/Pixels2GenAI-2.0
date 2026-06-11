/**
 * Build-time Open Graph image generation.
 *
 * Emits a 1200×630 PNG per lesson plus a site-wide default, served at
 *   /og/home.png          → site card (landing, generic pages)
 *   /og/lessons/<slug>.png → per-lesson card
 *
 * Cards are rendered with astro-og-canvas (CanvasKit/WASM) at build time —
 * no runtime cost. Brand palette mirrors src/styles/tokens.css.
 */

import { getCollection } from 'astro:content';
import { OGImageRoute } from 'astro-og-canvas';

const lessons = await getCollection('lessons');

// One entry per generated image. Keys become the URL path under /og/.
const pages: Record<string, { title: string; description: string }> = {
  home: {
    title: 'Pixels2GenAI',
    description:
      'An open curriculum from a single array element to building, training, and reasoning about modern generative models.',
  },
};

for (const lesson of lessons) {
  const slug = lesson.id.replace(/\.mdx?$/, '');
  pages[`lessons/${slug}`] = {
    title: `${slug} · ${lesson.data.title}`,
    description: lesson.data.objective,
  };
}

export const { getStaticPaths, GET } = await OGImageRoute({
  param: 'route',
  pages,
  // Default slug fn strips at the last dot, which mangles ids like "1.1.1".
  // Map the page key straight to "<key>.png" instead.
  getSlug: (path) => `${path}.png`,
  getImageOptions: (_path, page) => ({
    title: page.title,
    description: page.description,
    logo: undefined,
    bgGradient: [
      [17, 13, 22], // --bg
      [12, 9, 19], // --bg-deep
    ],
    border: { color: [181, 133, 232], width: 12, side: 'inline-start' }, // --c3
    padding: 80,
    font: {
      title: {
        color: [240, 231, 216], // --fg
        size: 64,
        weight: 'Bold',
        // lineHeight is a multiplier of font size, not pixels.
        lineHeight: 1.15,
        families: ['Literata', 'Georgia', 'serif'],
      },
      description: {
        color: [171, 162, 148], // --fg-2
        size: 30,
        lineHeight: 1.4,
        families: ['Plus Jakarta Sans', 'Helvetica', 'sans-serif'],
      },
    },
    fonts: [
      'https://api.fontsource.org/v1/fonts/literata/latin-700-normal.ttf',
      'https://api.fontsource.org/v1/fonts/plus-jakarta-sans/latin-400-normal.ttf',
    ],
  }),
});
