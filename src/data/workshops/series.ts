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
  /** The outcome in one line, for the card face (DEC-83). */
  cardMake: string;
  /** One line of context under the title on the home page mini cards (DEC-100). */
  homeLine: string;
  /** Equipment beyond a laptop with a browser (shown as "You need"). */
  needs?: string;
  /** Show "You need" on the card itself, not only behind "Inside" (W6: TouchDesigner, DEC-44). */
  needsOnCard?: boolean;
  /** Card image (public/workshops/series/one-photo/, 720 × 450 WebP): one source photo through each
   *  workshop's technique (DEC-90). Source: "Berliner Dom und Fernsehturm, 170117, ako.jpg", Ansgar Koreng,
   *  Wikimedia Commons, CC0. W5 shows the flow-matching path from noise to the photo (a real model image
   *  follows, BLD-23); W6 is a concept still until W6 is designed (BLD-25). */
  image: { src: string; alt: string; credit: string };
  warmup: string;
}

export const SERIES: SeriesWorkshop[] = [
  {
    id: 'w1', slug: 'w1-see', n: 1, verb: 'See', title: 'Pixel · Grid · Kernel', band: 'Foundations',
    date: 'Sat 5 Dec 2026', dateIso: '2026-12-05',
    idea: 'An image is a grid of numbers, and a kernel changes each pixel from its neighbours.',
    thread: null,
    threadText: 'The start of the series: no earlier idea needed.',
    cores: [
      { id: '1.1.1', title: 'Colour as numbers', sub: 'a pixel is three numbers; a channel-shift poster', minutes: 45, source: 'live' },
      { id: '3.4.1', title: 'Convolution', sub: 'a kernel reads the neighbours; you write the loop yourself', minutes: 55, source: 'live' },
      { id: '3.4.5', title: 'Dithering and halftone', sub: 'kernels for print', minutes: 50, source: 'new' },
    ],
    make: 'A print-ready riso-style image of your own photo; a photo print follows by post if you want one',
    cardMake: 'A riso-style print of your own photo',
    homeLine: 'An image is a grid of numbers',
    warmup: '3 quick questions: what is a pixel, what is 255, what is a neighbour?',
    image: { src: '/workshops/series/one-photo/w1.webp', alt: 'A riso-style print of the Berliner Dom and the Fernsehturm in pink and blue dots, made with a sharpening kernel and dithering.', credit: "Made with W1's lessons, from one photo" },
  },
  {
    id: 'w2', slug: 'w2-grow', n: 2, verb: 'Grow', title: 'Emergence', band: 'Foundations',
    date: 'Sat 9 Jan 2027', dateIso: '2027-01-09',
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
    cardMake: 'A one-colour line drawing of your photo, grown from a flow field',
    homeLine: 'Simple rules grow complex forms',
    warmup: '3 questions on kernels and neighbours',
    image: { src: '/workshops/series/one-photo/w2.webp', alt: "The Berliner Dom and the Fernsehturm drawn in thin blue lines that flow along the building's edges.", credit: "Made with W2's lessons, from one photo" },
  },
  {
    id: 'w3', slug: 'w3-sort', n: 3, verb: 'Sort', title: 'Patterns in data', band: 'Machine learning',
    date: 'Sat 6 Feb 2027', dateIso: '2027-02-06',
    idea: 'Pixels are points: similar ones are close, and you can measure how wrong a summary is.',
    thread: 'w2',
    threadText: 'From W2, iteration: k-means repeats one rule until the error stops falling.',
    cores: [
      { id: '3.3.4', title: 'Voronoi and stippling', sub: 'every pixel belongs to its nearest point', minutes: 50, source: 'leaf' },
      { id: '7.1.1', title: 'K-means palette', sub: 'move the points to lower the error', minutes: 50, source: 'leaf' },
      { id: '7.3.2', title: 'An image-embedding map', sub: 'a gallery sorted by what images look like', minutes: 55, source: 'leaf' },
    ],
    make: 'A stipple portrait or a sorted gallery poster',
    cardMake: 'A stipple print of your photo, with its own colour palette',
    homeLine: 'Sort pixels like data points',
    warmup: '3 questions on rules that repeat',
    image: { src: '/workshops/series/one-photo/w3.webp', alt: 'The Berliner Dom and the Fernsehturm as coloured stipple dots, with its five-colour palette in the corner.', credit: "Made with W3's lessons, from one photo" },
  },
  {
    id: 'w4', slug: 'w4-learn', n: 4, verb: 'Learn', title: 'The neuron', band: 'Machine learning',
    date: 'Sat 6 Mar 2027', dateIso: '2027-03-06',
    idea: 'Learning means nudging weights, again and again, to lower an error.',
    thread: 'w3',
    threadText: 'From W3, error; from W1, the weighted sum.',
    cores: [
      { id: '9.1.1', title: 'The perceptron', sub: 'a neuron that learns warm from cool', minutes: 50, source: 'live' },
      { id: '9.3.2', title: 'Watch the error fall', sub: 'a loss landscape and its descent', minutes: 50, source: 'leaf' },
      { id: '9.4.2', title: 'What a network sees', sub: 'feature maps of your own photo', minutes: 55, source: 'leaf' },
    ],
    make: 'A training animation or feature-map print',
    cardMake: 'Your photo as a neuron you trained sees it, plus its training animation',
    homeLine: 'Teach one neuron to see',
    warmup: '3 questions on distance and error',
    image: { src: '/workshops/series/one-photo/w4.webp', alt: 'The Berliner Dom in orange against a blue sky: what one trained neuron sees as warm or cool.', credit: "Made with W4's lessons, from one photo" },
  },
  {
    id: 'w5', slug: 'w5-dream', n: 5, verb: 'Dream', title: 'From noise to image', band: 'Generative AI',
    date: 'Sat 10 Apr 2027', dateIso: '2027-04-10',
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
    cardMake: 'Your sketch turned into an image by a real model',
    homeLine: 'A model turns your sketch into an image',
    needs: 'A laptop with a GPU, or a free Google Colab account',
    warmup: '3 questions on learning',
    image: { src: '/workshops/series/one-photo/w5.webp', alt: "The Berliner Dom and the Fernsehturm in six vertical bands, from pure noise on the left to the clear photo on the right.", credit: "Made with W5's maths, from one photo" },
  },
  {
    id: 'w6', slug: 'w6-play', n: 6, verb: 'Play', title: 'Live', band: 'Generative AI',
    date: 'Sat 8 May 2027', dateIso: '2027-05-08',
    idea: 'Input, process, output: every frame, in TouchDesigner.',
    thread: 'w5',
    threadText: 'Everything so far, running live.',
    cores: [
      { id: '10.1.1', title: 'Node networks', sub: 'the real-time loop', minutes: 45, source: 'live' },
      { id: '13.2.3', title: 'Your body drives the particles', sub: 'pose tracking meets GPU particles', minutes: 55, source: 'leaf' },
      { id: '13.3.4', title: 'Real-time diffusion', sub: 'your W5 style on the live camera', minutes: 55, source: 'new' },
    ],
    make: 'A recording of you inside your piece, plus a one-page capstone plan',
    cardMake: 'A recording of you inside your piece',
    homeLine: 'Real-time art you play with your body',
    needs: 'The free TouchDesigner on a laptop with a dedicated graphics card or a newer Mac. Setup steps follow before the workshop.',
    needsOnCard: true,
    warmup: '3 questions on the whole series',
    image: { src: '/workshops/series/one-photo/w6.webp', alt: "The Berliner Dom and the Fernsehturm as glowing particles in the photo's colours on a dark background.", credit: "Concept · particles in the photo's colours" },
  },
];

/** W7: capstone pieces shown together after W6 (DEC-16). On /workshops as the
 *  "empty wall" (W7d): one dashed frame per workshop, waiting for a piece. */
export const SHOWCASE = {
  title: 'Showcase',
  sub: 'W7 · capstone pieces, shown together',
  idea: "After W6 on 8 May, the pieces made across the series are shown together: prints, animations and recordings. Bring friends. You don't have to show anything to come.",
  date: 'June 2027',
  price: 'Free',
  note: 'Date and venue are not fixed yet.',
  cta: 'Hear when the date is set →', // no-break space keeps the arrow with its word
  frameText: 'your piece here',
};

/**
 * The day's timetable, shared by every workshop (03b §1, DEC-17): on-ramp,
 * three cores, make your piece, show and tell. `breakBefore` is the pause
 * before a block, in minutes (snacks throughout). Total 270 minutes = 4 h 30,
 * the prototype's 11:00–15:30 slot.
 */
export const DAY_PLAN = {
  start: '11:00',
  blocks: [
    { kind: 'onramp', minutes: 15, breakBefore: 0 },
    { kind: 'core', minutes: 55, breakBefore: 0 },
    { kind: 'core', minutes: 55, breakBefore: 10 },
    { kind: 'core', minutes: 55, breakBefore: 20 },
    { kind: 'make', minutes: 30, breakBefore: 15 },
    { kind: 'show', minutes: 15, breakBefore: 0 },
  ],
};

/** One line per kind of block, for the workshop-day graphic (`short` fits
 *  inside the timeline; `label` is used in the legend and on phones). */
export const DAY_KINDS = {
  onramp: { label: 'On-ramp', short: 'On-ramp', text: 'A quick recap and a 3-question warm-up' },
  core: { label: 'Core lesson', short: 'Core', text: 'Make it first, then understand it, step by step' },
  break: { label: 'Break', short: 'Break', text: 'Snacks and a stretch' },
  make: { label: 'Make your piece', short: 'Make', text: 'Your own work, from a short brief' },
  show: { label: 'Show and tell', short: 'Show', text: 'Share your piece, then one exit question' },
};

export const workshopBySlug = (slug: string) => SERIES.find((w) => w.slug === slug);
