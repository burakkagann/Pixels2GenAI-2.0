import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// Wrap content from each h2 to the next h2 in a <section class="lesson-section">.
// Drives the manuscript-margin-gloss side-rail (Option F) in prose.css —
// each section gets a vertical accent bar in the left gutter that auto-clips
// to the section's true height. Content before the first h2 (e.g. a hero
// Figure) is left at the article level, unwrapped.
function remarkSectionize() {
  return (tree) => {
    const newChildren = [];
    let currentSection = null;
    let idx = 0;

    for (const node of tree.children) {
      if (node.type === 'heading' && node.depth === 2) {
        if (currentSection) newChildren.push(currentSection);
        idx += 1;
        currentSection = {
          type: 'mdxJsxFlowElement',
          name: 'section',
          attributes: [
            { type: 'mdxJsxAttribute', name: 'class', value: 'lesson-section' },
            { type: 'mdxJsxAttribute', name: 'data-section', value: String(idx) },
          ],
          children: [node],
        };
      } else if (currentSection) {
        currentSection.children.push(node);
      } else {
        newChildren.push(node);
      }
    }
    if (currentSection) newChildren.push(currentSection);
    tree.children = newChildren;
  };
}

export default defineConfig({
  site: 'https://pixels2genai.art',
  markdown: {
    // Dual-theme Shiki: emits both palettes as CSS custom properties on each
    // token, then a CSS rule in prose.css swaps which set wins based on the
    // data-theme attribute on <html>.
    //
    // defaultColor:false is REQUIRED — without it Shiki writes the light theme
    // as literal inline `color`/`background-color` (with only the dark theme as
    // CSS vars). A bare ``` fence not wrapped in <CodeBlock> then keeps that
    // inline `background-color:#fff` and renders as a WHITE box in dark theme.
    // With defaultColor:false neither palette is inlined — both are emitted as
    // --shiki-light / --shiki-dark custom properties — so the swap rules in
    // prose.css govern every block (wrapped or bare) and the white-box bug
    // cannot recur. See prose.css ".astro-code" dual-theme block.
    shikiConfig: {
      // github-light-high-contrast keeps every token at WCAG AA even on a WARM
      // CREAM code surface (stock github-light and github-light-default both
      // drop the keyword/comment tokens below 4.5:1 on cream — only the
      // high-contrast palette holds). github-dark is unchanged for dark theme.
      themes: { light: 'github-light-high-contrast', dark: 'github-dark' },
      defaultColor: false,
    },
  },
  integrations: [
    react(),
    mdx({ remarkPlugins: [remarkSectionize] }),
    sitemap({
      // The /og/*.png endpoints are social-card images, not crawlable pages.
      filter: (page) => !page.includes('/og/'),
    }),
  ],
  vite: {
    resolve: {
      alias: {
        '@': '/src',
      },
    },
  },
});
