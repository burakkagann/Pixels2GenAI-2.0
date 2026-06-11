/**
 * Module catalog — 15 modules + capstone.
 *
 * `firstLesson` points to a lesson slug that exists in v2 (under
 * src/content/lessons/<slug>.mdx). When set, the module card links to
 * that lesson. When undefined the card renders as "Coming soon".
 *
 * Framework labels:
 *   F1 = Hands-On Discovery
 *   F2 = Conceptual Deep-Dive
 *   F3 = Project-Based (capstone)
 */

export interface ModuleEntry {
  idx: string;            // "00".."15"
  title: string;          // first line of the card
  em: string;             // second line, italicized
  fw: 'F1' | 'F2' | 'F1+F2' | 'F3';
  /** Stage: I (Foundations), II (Machine Learning), III (Generative AI). Drives accent color. */
  cycle: 'I' | 'II' | 'III';
  /** Slug of the lesson the card should link to. Undefined → "Coming soon". */
  firstLesson?: string;
  capstone?: boolean;
}

export const MODULES: ModuleEntry[] = [
  { idx: '00', title: 'Foundations',       em: '& Definitions',       fw: 'F2',    cycle: 'I' },
  { idx: '01', title: 'Pixel',             em: 'Fundamentals',        fw: 'F1',    cycle: 'I',   firstLesson: '1.1.1' },
  { idx: '02', title: 'Geometry',          em: '& Mathematics',       fw: 'F1',    cycle: 'I' },
  { idx: '03', title: 'Transformations',   em: '& Effects',           fw: 'F1',    cycle: 'I' },
  { idx: '04', title: 'Fractals',          em: '& Recursion',         fw: 'F1+F2', cycle: 'I',   firstLesson: '4.1.1' },
  { idx: '05', title: 'Simulation',        em: 'Emergent Behavior',   fw: 'F1',    cycle: 'I' },
  { idx: '06', title: 'Noise',             em: '& Procedural Gen.',   fw: 'F1',    cycle: 'II' },
  { idx: '07', title: 'Classical ML',      em: 'on Images',           fw: 'F2',    cycle: 'II' },
  { idx: '08', title: 'Animation',         em: '& Time',              fw: 'F1',    cycle: 'II' },
  { idx: '09', title: 'Neural',            em: 'Networks',            fw: 'F2',    cycle: 'II' },
  { idx: '10', title: 'Touch',             em: 'Designer',            fw: 'F2',    cycle: 'II' },
  { idx: '11', title: 'Interactive',       em: 'Systems',             fw: 'F1',    cycle: 'II' },
  { idx: '12', title: 'Generative AI',     em: 'Models',              fw: 'F2',    cycle: 'III', firstLesson: '12.1.2' },
  { idx: '13', title: 'AI +',              em: 'TouchDesigner',       fw: 'F2',    cycle: 'III' },
  { idx: '14', title: 'Data',              em: 'as Material',         fw: 'F1',    cycle: 'III' },
  { idx: '15', title: 'Capstone',          em: 'Project',             fw: 'F3',    cycle: 'III', capstone: true },
];

/**
 * Sliding window of `size` modules centred on `currentIdx`,
 * clamped to [0, MODULES.length - 1]. Powers the lesson-page stage
 * tracker — at the edges, the window slides inward so it always
 * returns exactly `size` modules (assuming MODULES.length >= size).
 */
export function windowAround(currentIdx: number, size = 8): ModuleEntry[] {
  let start = currentIdx - Math.floor((size - 1) / 2);
  let end = start + size - 1;
  if (start < 0) { end -= start; start = 0; }
  if (end > MODULES.length - 1) { start -= end - (MODULES.length - 1); end = MODULES.length - 1; }
  start = Math.max(0, start);
  return MODULES.slice(start, end + 1);
}

/** Resolve a frontmatter `module` label like "M 04" to a numeric index. */
export function moduleIndexFromLabel(label: string): number {
  const m = label.match(/(\d+)/);
  return m ? parseInt(m[1], 10) : 0;
}
