/**
 * Five Research Questions and three DBR Cycles that anchor the Research
 * section on the landing page. Drawn from the project's CLAUDE.md.
 */

export interface RQEntry {
  tag: string;       // "RQ 1"
  title: string;     // short heading
  question: string;  // italic body (full formal RQ; also shown on /research)
  gloss: string;     // one-line plain-language version shown on the landing card
}

export const RQS: RQEntry[] = [
  {
    tag: 'RQ 1',
    title: 'Framework design',
    question:
      'What pedagogical principles and design patterns effectively scaffold learning progressions from basic array manipulation to generative AI in creative contexts?',
    gloss: 'Which teaching patterns best scaffold the climb from arrays to generative AI?',
  },
  {
    tag: 'RQ 2',
    title: 'Cognitive load',
    question:
      'How can complex technical concepts be decomposed and sequenced to maintain optimal cognitive load while building toward advanced applications?',
    gloss: 'How should hard concepts be split and sequenced so novices avoid overload?',
  },
  {
    tag: 'RQ 3',
    title: 'Integration paths',
    question:
      'What strategies effectively integrate real-time systems with progressive AI learning, and at what points in the curriculum should these integrations occur?',
    gloss: 'When and how should real-time systems join the learning path?',
  },
  {
    tag: 'RQ 4',
    title: 'Assessment',
    question:
      'How can learning outcomes in creative AI education be assessed across technical proficiency, creative expression, and conceptual understanding?',
    gloss: 'How do you measure technical skill, creativity, and understanding together?',
  },
  {
    tag: 'RQ 5',
    title: 'Transfer',
    question:
      'To what extent do learners successfully transfer foundational computational concepts to novel creative AI contexts, and what factors facilitate this transfer?',
    gloss: 'Do learners carry core concepts into new creative AI work, and what helps?',
  },
];

export interface CycleEntry {
  label: string;
  modules: string;
  cycle: 'c1' | 'c2' | 'c3';
  /** Display name, identical to label here (kept for API compatibility with callers that use `.name`). */
  name: string;
  /** One-sentence pitch shown in the § 2 Curriculum station header. */
  pitch: string;
}

export const CYCLES: CycleEntry[] = [
  {
    label: 'Foundations',
    name: 'Foundations',
    pitch: 'Pixels, geometry, recursion, simulation. NumPy and PIL only, no networks yet. Visual intuition first.',
    modules: 'Modules 00 – 05',
    cycle: 'c1',
  },
  {
    label: 'Machine Learning',
    name: 'Machine Learning',
    pitch: 'Procedural generation, classical ML, animation, first neural networks, real-time. Arrays become inference.',
    modules: 'Modules 06 – 11',
    cycle: 'c2',
  },
  {
    label: 'Generative AI',
    name: 'Generative AI',
    pitch: 'GANs, VAEs, diffusion, language models, integration, capstone. The generative stack, end to end.',
    modules: 'Modules 12 – 15',
    cycle: 'c3',
  },
];
