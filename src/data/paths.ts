/**
 * The three learning paths displayed in the Paths section of the landing page.
 * Each path bundles modules into a directed reading order.
 */

export interface PathEntry {
  tag: string;
  title: string;
  em: string;
  description: string;
  steps: Array<{ ix: string; label: string }>;
  meta: string[];
  cycle: 'c1' | 'c2' | 'c3';
  persona: 'painter' | 'engineer' | 'architect';
}

export const PATHS: PathEntry[] = [
  {
    tag: 'Foundations',
    title: 'The Painter',
    em: 'arrays & shapes',
    description:
      'For learners who want to see results immediately. NumPy + PIL only, no networks. Build intuition for pixels, geometry, transforms, fractals, and simulation before touching machine learning.',
    steps: [
      { ix: 'M 01', label: 'Pixel fundamentals' },
      { ix: 'M 02', label: 'Geometry & math' },
      { ix: 'M 03', label: 'Transformations' },
      { ix: 'M 04', label: 'Fractals & recursion' },
      { ix: 'M 05', label: 'Simulation' },
      { ix: 'M 06', label: 'Noise & procedural' },
    ],
    meta: ['~2 h', 'Modules 1 – 6', 'Hands-on'],
    cycle: 'c1',
    persona: 'painter',
  },
  {
    tag: 'Advanced',
    title: 'The Engineer',
    em: 'algorithms & networks',
    description:
      'For programmers who already speak NumPy. Skip the painting modules, jump to classical ML, animation, and neural networks. You will still produce visual artifacts — they will just teach you the algorithm underneath.',
    steps: [
      { ix: 'M 07', label: 'Classical ML on images' },
      { ix: 'M 08', label: 'Animation & time' },
      { ix: 'M 09', label: 'Intro to neural nets' },
      { ix: 'M 10', label: 'TouchDesigner basics' },
      { ix: 'M 11', label: 'Interactive systems' },
    ],
    meta: ['~3 h', 'Modules 7 – 11', 'Deep-dive'],
    cycle: 'c2',
    persona: 'engineer',
  },
  {
    tag: 'AI / ML',
    title: 'The Architect',
    em: 'generative models',
    description:
      'For learners with a CS background coming for generative AI. GANs, VAEs, diffusion, CLIP, and integration with real-time systems. The capstone synthesizes everything into a portfolio-ready project.',
    steps: [
      { ix: 'M 12', label: 'Generative AI models' },
      { ix: 'M 13', label: 'AI + TouchDesigner' },
      { ix: 'M 14', label: 'Data as material' },
      { ix: 'M 15', label: 'Capstone project' },
    ],
    meta: ['~3 h', 'Modules 12 – 15', 'Project'],
    cycle: 'c3',
    persona: 'architect',
  },
];
