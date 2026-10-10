/**
 * The six-workshop series (research cycle ii): one source for the public
 * /workshops page, the arc pages and the series map.
 *
 * Pure data, no type annotations inside the literal: scripts/lib/catalog.mjs
 * reads SERIES the same way it reads subtopics.ts, and check-lessons.mjs
 * verifies every core id against the curriculum catalog.
 *
 * Core lesson ids are placeholders until the module ids are redesigned after
 * the series. `source` says how each id relates to the catalog today:
 *   live = a shipped lesson (/lessons/<id>); the workshop version is a rework
 *   leaf = a catalog leaf with no lesson yet
 *   new  = not in the catalog; added to subtopics.ts when the lesson goes public
 *
 * Dates stay 'TBA' until each workshop is booked; dateIso unlocks the
 * date-based rules (arc opens on the day, everything open after it).
 */

export type WorkshopId = 'w1' | 'w2' | 'w3' | 'w4' | 'w5' | 'w6';
export type CoreSource = 'live' | 'leaf' | 'new';

export interface WorkshopCore {
  /** Curriculum-style lesson id; also the URL segment /workshops/<slug>/<id>. */
  id: string;
  title: string;
  /** One line under the title on the arc page. */
  sub: string;
  minutes: number;
  source: CoreSource;
}

export interface SeriesWorkshop {
  id: WorkshopId;
  /** URL segment: /workshops/w1-see. */
  slug: string;
  n: number;
  verb: string;
  title: string;
  /** Curriculum stage the workshop sits in. */
  band: 'Foundations' | 'Machine learning' | 'Generative AI';
  /** Human-readable; 'TBA' until booked. */
  date: string;
  dateIso?: string;
  /** The one idea of the day, in one sentence. */
  idea: string;
  /** The earlier workshop this one builds on (null for W1). */
  thread: WorkshopId | null;
  /** The on-ramp recap line. */
  threadText: string;
  cores: [WorkshopCore, WorkshopCore, WorkshopCore];
  /** The make-your-piece brief. */
  make: string;
  warmup: string;
}

export const SERIES: SeriesWorkshop[] = [
  {
    id: 'w1', slug: 'w1-see', n: 1, verb: 'See', title: 'Pixel · Grid · Kernel', band: 'Foundations',
    date: 'TBA',
    idea: 'An image is a grid of numbers, and a kernel changes each pixel from its neighbours.',
    thread: null,
    threadText: 'The start of the series: no earlier idea needed.',
    cores: [
      { id: '1.1.1', title: 'Colour as numbers', sub: 'a pixel is three numbers; a channel-shift poster', minutes: 45, source: 'live' },
      { id: '3.4.1', title: 'Convolution', sub: 'a kernel reads the neighbours; you write the loop yourself', minutes: 55, source: 'live' },
      { id: '3.4.5', title: 'Dithering and halftone', sub: 'kernels for print', minutes: 50, source: 'new' },
    ],
    make: 'A riso-style print or zine page of your own photo',
    warmup: '3 quick questions: what is a pixel, what is 255, what is a neighbour?',
  },
  {
    id: 'w2', slug: 'w2-grow', n: 2, verb: 'Grow', title: 'Emergence', band: 'Foundations',
    date: 'TBA',
    idea: 'A simple rule, applied again and again, makes complex form.',
    thread: 'w1',
    threadText: 'From W1, the kernel: the Game of Life counts neighbours with one.',
    cores: [
      { id: '1.2.2', title: 'Cellular automata', sub: 'rules over a grid, generation by generation', minutes: 50, source: 'live' },
      // Outline v2 leaves 4.2.1 or 4.1.1 open; 4.2.1 until decided.
      { id: '4.2.1', title: 'Fractal trees', sub: 'a rule that calls itself', minutes: 45, source: 'live' },
      { id: '6.3.5', title: 'Flow fields', sub: 'noise-driven lines, ready for a pen plotter', minutes: 55, source: 'new' },
    ],
    make: 'A one-line, one-colour piece: print or animated',
    warmup: '3 questions on kernels and neighbours',
  },
  {
    id: 'w3', slug: 'w3-sort', n: 3, verb: 'Sort', title: 'Patterns in data', band: 'Machine learning',
    date: 'TBA',
    idea: 'Pixels are points: similar ones are close, and you can measure how wrong a summary is.',
    thread: 'w2',
    threadText: 'From W2, iteration: k-means repeats one rule until the error stops falling.',
    cores: [
      { id: '3.3.4', title: 'Voronoi and stippling', sub: 'every pixel belongs to its nearest point', minutes: 50, source: 'leaf' },
      { id: '7.1.1', title: 'K-means palette', sub: 'move the points to lower the error', minutes: 50, source: 'leaf' },
      { id: '7.3.2', title: 'An image-embedding map', sub: 'a gallery sorted by what images look like', minutes: 55, source: 'leaf' },
    ],
    make: 'A stipple portrait or a sorted gallery poster',
    warmup: '3 questions on rules that repeat',
  },
  {
    id: 'w4', slug: 'w4-learn', n: 4, verb: 'Learn', title: 'The neuron', band: 'Machine learning',
    date: 'TBA',
    idea: 'Learning means nudging weights, again and again, to lower an error.',
    thread: 'w3',
    threadText: 'From W3, error; from W1, the weighted sum.',
    cores: [
      { id: '9.1.1', title: 'The perceptron', sub: 'a neuron that learns warm from cool', minutes: 50, source: 'live' },
      { id: '9.3.2', title: 'Watch the error fall', sub: 'a loss landscape and its descent', minutes: 50, source: 'leaf' },
      { id: '9.4.2', title: 'What a network sees', sub: 'feature maps of your own photo', minutes: 55, source: 'leaf' },
    ],
    make: 'A training animation or feature-map print',
    warmup: '3 questions on distance and error',
  },
  {
    id: 'w5', slug: 'w5-dream', n: 5, verb: 'Dream', title: 'From noise to image', band: 'Generative AI',
    date: 'TBA',
    idea: 'A trained network turns noise into an image, step by step.',
    thread: 'w4',
    threadText: 'From W2, noise; from W4, a network that learns.',
    cores: [
      { id: '12.2.4', title: 'Latent space by hand', sub: 'images as points on a learned map', minutes: 50, source: 'new' },
      { id: '12.7.2', title: 'Flow matching from scratch', sub: 'noise becomes points, then pictures', minutes: 55, source: 'new' },
      // ControlNet until decided; a LoRA core would become a new leaf (e.g. 12.5.2).
      { id: '12.3.2', title: 'A real model', sub: 'your sketch or style, turned into an image', minutes: 55, source: 'live' },
    ],
    make: 'Your sketch or your style turned into an image, labelled as AI-made',
    warmup: '3 questions on learning',
  },
  {
    id: 'w6', slug: 'w6-play', n: 6, verb: 'Play', title: 'Live', band: 'Generative AI',
    date: 'TBA',
    idea: 'Input, process, output: every frame, in TouchDesigner.',
    thread: 'w5',
    threadText: 'Everything so far, running live.',
    cores: [
      { id: '10.1.1', title: 'Node networks', sub: 'the real-time loop', minutes: 45, source: 'live' },
      { id: '13.2.3', title: 'Your body drives the particles', sub: 'pose tracking meets GPU particles', minutes: 55, source: 'leaf' },
      { id: '13.3.4', title: 'Real-time diffusion', sub: 'your W5 style on the live camera', minutes: 55, source: 'new' },
    ],
    make: 'A recording of you inside your piece, plus a one-page capstone plan',
    warmup: '3 questions on the whole series',
  },
];

/** W7: capstone pieces shown together after W6 (DEC-16). */
export const SHOWCASE = { title: 'Showcase', sub: 'W7 · capstone pieces, shown together', date: 'TBA' };

/**
 * The day's timetable, shared by every workshop (03b §1): on-ramp, three
 * cores, make your piece, show and tell. `breakBefore` is the pause before a
 * block, in minutes. From 11:00 this ends at 15:10; the prototype's
 * "11:00–15:30" slot leaves 20 minutes of slack.
 */
export const DAY_PLAN = {
  start: '11:00',
  blocks: [
    { kind: 'onramp', minutes: 15, breakBefore: 0 },
    { kind: 'core', minutes: 55, breakBefore: 0 },
    { kind: 'core', minutes: 55, breakBefore: 10 },
    { kind: 'core', minutes: 55, breakBefore: 15 },
    { kind: 'make', minutes: 30, breakBefore: 0 },
    { kind: 'show', minutes: 15, breakBefore: 0 },
  ],
};

export const workshopBySlug = (slug: string) => SERIES.find((w) => w.slug === slug);
