import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import mdx from '@astrojs/mdx';

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
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },
  integrations: [react(), mdx({ remarkPlugins: [remarkSectionize] })],
  vite: {
    resolve: {
      alias: {
        '@': '/src',
      },
    },
  },
});
