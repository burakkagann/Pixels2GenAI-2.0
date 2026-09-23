/**
 * Search-snippet text for a lesson: its `description` frontmatter when set,
 * otherwise the (plain-text) objective trimmed to fit.
 *
 * Google truncates meta descriptions at roughly 155-160 characters with "…".
 * Rather than let it cut mid-word, end on the last full sentence that fits;
 * if no sentence fits with enough substance left, cut at a word boundary and
 * add the ellipsis ourselves. JSON-LD and RSS keep the full objective.
 */
export const META_DESCRIPTION_MAX = 160;

export function metaDescription(plainObjective: string, description?: string): string {
  if (description) return description;
  const text = plainObjective.trim();
  if (text.length <= META_DESCRIPTION_MAX) return text;

  // Last sentence end (. ! ?) followed by a space, within the limit.
  const window = text.slice(0, META_DESCRIPTION_MAX + 1);
  const sentenceEnd = Math.max(...['. ', '! ', '? '].map((p) => window.lastIndexOf(p)));
  if (sentenceEnd >= 70) return text.slice(0, sentenceEnd + 1);

  // Next best: end at the last clause break ("X, then Y", "X — aside — Y",
  // "X; Y") with a full stop. Objectives are written as chained clauses, so
  // the text before the break is normally a complete sentence on its own.
  const clauseEnd = Math.max(...[', then ', '; ', ' — ', ', and then '].map((p) => window.lastIndexOf(p)));
  if (clauseEnd >= 90) return text.slice(0, clauseEnd).replace(/[,;:]$/, '') + '.';

  // Otherwise the last whole word, plus an ellipsis.
  const cut = text.slice(0, META_DESCRIPTION_MAX - 1);
  const lastSpace = cut.lastIndexOf(' ');
  return cut.slice(0, lastSpace > 0 ? lastSpace : cut.length).replace(/[\s,;:—–-]+$/, '') + '…';
}
