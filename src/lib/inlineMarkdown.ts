/**
 * Minimal inline Markdown for plain-string lesson fields: frontmatter
 * `objective` and the `caption` / `title` / `summary` props of the MDX
 * components. Those strings never pass through remark, so `code` and *em*
 * written in them used to print their backticks and asterisks literally.
 *
 * Supports exactly what the lessons use: `code`, **strong**, *em*.
 * - inlineMarkdownHtml(): HTML-escaped first, then those three wrapped in
 *   tags. Safe for set:html because every character of the input is escaped
 *   before any tag is added.
 * - inlineMarkdownText(): the same string with the markers removed, for
 *   places that need plain text (meta description, JSON-LD, RSS, OG image).
 */

const escapeHtml = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Asterisk emphasis must hug its content (no inner-edge spaces), so an
// arithmetic "2 * 3 * 4" is left alone.
const STRONG = /\*\*(?=\S)([^*]*?\S)\*\*/g;
const EM = /(^|[^*\w])\*(?=[^\s*])([^*]*?[^\s*])\*(?!\*)/g;

export function inlineMarkdownHtml(input: string): string {
  // Split on code spans first: nothing inside backticks is emphasis.
  return input
    .split(/(`[^`]+`)/)
    .map((part) => {
      if (part.length > 2 && part.startsWith('`') && part.endsWith('`')) {
        return `<code>${escapeHtml(part.slice(1, -1))}</code>`;
      }
      return escapeHtml(part).replace(STRONG, '<strong>$1</strong>').replace(EM, '$1<em>$2</em>');
    })
    .join('');
}

export function inlineMarkdownText(input: string): string {
  return input
    .split(/(`[^`]+`)/)
    .map((part) =>
      part.length > 2 && part.startsWith('`') && part.endsWith('`')
        ? part.slice(1, -1)
        : part.replace(STRONG, '$1').replace(EM, '$1$2'),
    )
    .join('');
}
