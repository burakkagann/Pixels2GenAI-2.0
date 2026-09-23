import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

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
  // One canonical URL form, enforced at every layer. The whole site's internal
  // links and JSON-LD already emit no-trailing-slash paths (/lessons/2.1.1), but
  // the default 'directory' build format served every page from an index.html at
  // /lessons/2.1.1/ — so Google reached the no-slash form via our own links,
  // got 301'd to the slash form, and logged the no-slash URL as "Page with
  // redirect" (26 of them). 'file' format emits /lessons/2.1.1.html (served at
  // /lessons/2.1.1), and 'never' makes Astro.url + @astrojs/sitemap agree on the
  // no-slash form, so links, canonical tag, and sitemap all match. See Google's
  // "To slash or not to slash": pick one form, use it everywhere.
  trailingSlash: 'never',
  build: { format: 'file' },
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
      // high-contrast palette holds). Dark uses github-dark-default: the older
      // github-dark's comment grey #6A737D was 3.6:1 on the warm --code-surface
      // (#1E1A14); -default's #8B949E is 5.6:1 and every other token is >= 6.9:1.
      themes: { light: 'github-light-high-contrast', dark: 'github-dark-default' },
      defaultColor: false,
    },
  },
  integrations: [
    react(),
    // remark-math parses $…$ / $$…$$ in lesson prose into math nodes (before
    // MDX escape handling, so `\,` and `\theta` survive); rehype-katex renders
    // them to static HTML at build time, no client JS. KaTeX CSS is imported
    // by Lesson.astro. A literal dollar sign in prose must be written `\$`.
    // Frontmatter strings and component props (objective, caption=…) are not
    // Markdown and are not rendered: keep them plain text.
    mdx({ remarkPlugins: [remarkSectionize, remarkMath], rehypePlugins: [rehypeKatex] }),
    sitemap({
      // The /og/*.png endpoints are social-card images, not crawlable pages.
      // /announce/thanks (form confirmation) and /404 are noindex pages.
      filter: (page) => !page.includes('/og/') && !/\/(announce\/thanks|404)(\.html)?$/.test(page),
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
