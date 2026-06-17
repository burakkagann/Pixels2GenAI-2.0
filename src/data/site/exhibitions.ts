/**
 * Pixels2GenAI exhibitions — one-off group shows co-organised with Academis,
 * showing printed and code-driven work side by side. Each exhibition has its
 * own dedicated route at /exhibitions/<id>. The landing page's § 4 Exhibition
 * section is the catalog entry that links into the per-show page.
 */

export type ExhibitionStatus = 'past' | 'upcoming';

export interface ExhibitionArtist {
  name: string;
  /** Optional one-line role or contribution note. Omit for "contributing artist" placeholder. */
  role?: string;
}

export interface ExhibitionPrintedWork {
  id: string;
  title: string;
  /** Italic em subtitle ("void", "bloom", "ReLU"). */
  subtitle?: string;
  artist: string;
  /**
   * One-line technique summary (mono micro-typography in card caption).
   * Optional: title-only works (e.g. a guest artist's prints, pending their
   * own technique note) omit it and the caption/modal hide the line.
   */
  technique?: string;
  /** Longer description for the modal. */
  description?: string;
  /** Public path to the image asset. */
  src: string;
  year?: string;
  dimensions?: string;
}

export interface ExhibitionAnimatedWork {
  id: string;
  title: string;
  subtitle?: string;
  artist: string;
  technique: string;
  description: string;
  githubUrl: string;
  /** Public path to a still frame. Absent → typographic placeholder. */
  stillSrc?: string;
  /** Optional second still used to simulate the hover-to-play affordance. */
  hoverSrc?: string;
  /**
   * Public path to a looping capture (muted, playsinline). When present, the
   * per-show card renders an autoplaying <video> with `stillSrc` as its poster
   * and reduced-motion fallback; the landing strip still shows the poster only.
   */
  videoSrc?: string;
  status: 'capture-available' | 'capture-pending';
}

/**
 * Editorial grouping for the per-show print gallery. `printedWorks` stays the
 * flat source of truth (the lightbox modal and landing strip resolve works by
 * `id`); `printSeries` only drives how the `#prints` section is clustered into
 * titled series. Mirrors the curriculum's `{ id, title, children[] }` shape.
 */
export interface ExhibitionPrintSeries {
  id: string;
  /** Display heading for the cluster. */
  title: string;
  /** One-line curatorial statement (drawn from the printed wall text). */
  statement?: string;
  /** Ordered `printedWorks` ids shown under this series. */
  workIds: string[];
  /** Guest-artist credit; when set with `artistUrl`, the heading links out. */
  artist?: string;
  artistUrl?: string;
}

export interface Exhibition {
  id: string;
  /** Roman lowercase ordinal — matches the workshops register. */
  ordinal: string;
  status: ExhibitionStatus;

  date: string;
  dateIso: string;
  openingHours: string;
  publicHours: string;
  admission: string;

  city: string;
  district?: string;
  venue: string;
  station?: string;
  address: string;

  poster: string;
  posterPdf?: string;
  posterCaption?: string;

  organiser: string;
  organiserHref: string;

  /** Statement paragraphs — the first paragraph gets a drop-cap. */
  statement: string[];

  artists: ExhibitionArtist[];
  /**
   * Curators credited on the per-show page. Rendered as a separate
   * sub-block below the artists grid (`.exhibition-curators-block`).
   */
  curators: ExhibitionArtist[];
  printedWorks: ExhibitionPrintedWork[];
  animatedWorks: ExhibitionAnimatedWork[];

  /**
   * Editorial clustering of `printedWorks` into titled series for the per-show
   * gallery. When undefined, the page falls back to one flat plate grid.
   */
  printSeries?: ExhibitionPrintSeries[];

  /**
   * Ordered list of work `id`s (mixing printedWorks and animatedWorks) shown
   * in the landing § 4 specimen's plate strip. Curation is editorial — when
   * undefined, the component falls back to first-three prints + first
   * animated-with-still + first capture-pending.
   */
  landingPlates?: string[];
}

export const EXHIBITIONS: Exhibition[] = [
  {
    id: 'exhibition-2026-03',
    ordinal: 'i',
    status: 'past',
    date: 'March 27, 2026',
    dateIso: '2026-03-27',
    openingHours: 'March 27 · 18:00 — opening',
    publicHours: 'March 28 · 10:00–16:00 — public',
    admission: 'Free',
    city: 'Berlin',
    district: 'Schöneberg',
    venue: 'IT studio Academis',
    station: 'U Kleistpark',
    address: 'Steinmetzstrasse 40',
    poster: '/exhibitions/poster-2026-03.png',
    posterPdf: '/exhibitions/poster-2026-03.pdf',
    posterCaption: 'Poster · Pixels2GenAI · March 27',
    organiser: 'Academis · Kristian Rother',
    organiserHref: 'https://www.academis.eu',
    statement: [
      'Pixels2GenAI is an exhibition by software developers creating computer art. The works on view use equations, algorithms, and AI models to generate images and installations — exploring the space between hand-programmed images, the aesthetics of mathematical rules, and AI as an art-making tool.',
      'At the end of March 2026, the office of IT studio Academis transformed into a gallery for two days — an opening evening for invited guests, then a day open to the public.',
    ],
    artists: [
      { name: 'Burak Kağan Yılmazer', role: 'Project author' },
      { name: 'Sara Maras' },
      { name: 'Alexander Hendorf' },
      { name: 'Hansu Kim' },
      { name: 'Maris Nieuwenhuis' },
      { name: 'Ewa Rother' },
    ],
    curators: [
      { name: 'Kristian Rother', role: 'Co-curator' },
      { name: 'Ewa Rother', role: 'Co-curator' },
    ],
    printedWorks: [
      {
        id: 'array-zero-void',
        title: 'Array Zero',
        subtitle: 'void',
        artist: 'Burak Kağan Yılmazer',
        technique: 'NumPy · np.zeros() · printed on paper',
        description: 'Every digital image begins as an array of zeros. canvas = np.zeros((4096, 4096, 3)) — the void before the first pixel of light. The opening frame of the series, and the first lesson of the Pixels2GenAI platform.',
        src: '/exhibitions/prints/array-zero-01-void.jpg',
      },
      {
        id: 'array-zero-spark',
        title: 'Array Zero',
        subtitle: 'spark',
        artist: 'Burak Kağan Yılmazer',
        technique: 'NumPy · Gaussian falloff · printed on paper',
        description: 'A single NumPy operation places the first pixel of light. A Gaussian falloff — glow = 255 · exp(−½ (distance / σ)²) — radiates from the centre of the zero array. The code that drew it is printed onto the canvas.',
        src: '/exhibitions/prints/array-zero-02-spark.jpg',
      },
      {
        id: 'array-zero-bloom',
        title: 'Array Zero',
        subtitle: 'radial bloom',
        artist: 'Burak Kağan Yılmazer',
        technique: 'NumPy · meshgrid + exponential decay · printed on paper',
        description: 'The spark expands. The same Gaussian field bloomed across the canvas through meshgrid coordinates and exponential decay — the seed pixel grown into a radial disc of light.',
        src: '/exhibitions/prints/array-zero-03-bloom.jpg',
      },
      {
        id: 'array-zero-spiral-bloom',
        title: 'Array Zero',
        subtitle: 'spiral bloom',
        artist: 'Burak Kağan Yılmazer',
        technique: 'NumPy · polar coordinates + arctangent · printed on paper',
        description: 'Polar coordinates spin colour into existence: an arctangent angle, twisted by distance and wrapped to [0, 1], mapped through a warm-ember gradient. The void fully bloomed — the final frame of the series. Generative art begins not with inspiration but with np.zeros().',
        src: '/exhibitions/prints/array-zero-04-spiral-bloom.jpg',
      },
      {
        id: 'tectonic-threshold-relu',
        title: 'Tectonic Threshold',
        subtitle: 'ReLU',
        artist: 'Burak Kağan Yılmazer',
        technique: 'ReLU activation over layered trigonometry · printed on paper',
        description: 'Neural networks pass signals through activation functions — mathematical gates deciding what flows forward. ReLU discards everything negative, and the kink at zero becomes a geological fault. One activation applied to layered trigonometric compositions at rising frequencies, building terrain from pure mathematics.',
        src: '/exhibitions/prints/tectonic-threshold-relu.jpg',
      },
      {
        id: 'tectonic-threshold-sigmoid',
        title: 'Tectonic Threshold',
        subtitle: 'sigmoid',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Sigmoid activation over layered trigonometry · printed on paper',
        description: 'The same operation under the sigmoid activation. Sigmoid compresses its input into a smooth curve, and the fault smooths into a soft ridge. The geological resemblance is not accidental — threshold functions across scales share the structure of tectonic processes.',
        src: '/exhibitions/prints/tectonic-threshold-sigmoid.jpg',
      },
      {
        id: 'tectonic-threshold-tanh',
        title: 'Tectonic Threshold',
        subtitle: 'tanh',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Tanh activation over layered trigonometry · printed on paper',
        description: 'f(x) = (eˣ − e⁻ˣ) / (eˣ + e⁻ˣ): the hyperbolic tangent stretches the boundary symmetrically about zero, so positive and negative inputs mirror into balanced ridges and basins. The same layered trigonometric field as its ReLU and sigmoid siblings, resolved into a symmetric, contour-mapped terrain.',
        src: '/exhibitions/prints/tectonic-threshold-tanh.jpg',
      },
      {
        id: 'orbit-sediment-trichrome',
        title: 'Orbit Sediment',
        subtitle: 'trichrome',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Clifford · De Jong · Svensson attractors → RGB channels · Perlin displacement',
        description: 'Three strange attractors — Clifford, De Jong, Svensson — layered into separate red, green, and blue channels for iridescent interference, then displaced by turbulent Perlin noise into organic ridges. Violet, amber, and cyan orbits overlap where the three systems cross. Over 10 million iterations per print.',
        src: '/exhibitions/prints/orbit-sediment-trichrome.jpg',
      },
      {
        id: 'orbit-sediment-widespread',
        title: 'Orbit Sediment',
        subtitle: 'widespread',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Clifford attractor · turbulent Perlin displacement · printed on paper',
        description: 'A single Clifford attractor — x = sin(a·y) + c·cos(a·x), y = sin(b·x) + d·cos(b·y) — a deterministic system tracing never-repeating orbits, spread wide across the field and displaced by turbulent noise into pale, sedimentary filaments. Over 10 million iterations.',
        src: '/exhibitions/prints/orbit-sediment-widespread.jpg',
      },
      {
        id: 'orbit-sediment-dualglow',
        title: 'Orbit Sediment',
        subtitle: 'dual glow',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Clifford attractor · turbulent Perlin displacement · printed on paper',
        description: 'The same deterministic orbits resolved into a warm core glowing against cooler blue wings — two registers of the one attractor, displaced by Perlin noise into ridged sediment. Over 10 million iterations.',
        src: '/exhibitions/prints/orbit-sediment-dualglow.jpg',
      },
      {
        id: 'maris-menger-flake',
        title: 'Menger Flake',
        artist: 'Maris Nieuwenhuis',
        src: '/exhibitions/prints/maris-menger-flake.jpg',
      },
      {
        id: 'maris-koch-3d',
        title: 'Koch Curve',
        artist: 'Maris Nieuwenhuis',
        src: '/exhibitions/prints/maris-koch-3d.jpg',
      },
      {
        id: 'maris-scene-rework',
        title: 'Scene Rework',
        artist: 'Maris Nieuwenhuis',
        src: '/exhibitions/prints/maris-scene-rework.jpg',
      },
    ],
    animatedWorks: [
      {
        id: 'neural-mycelium',
        title: 'Neural-Mycelium',
        subtitle: 'metabolic rate',
        artist: 'Burak Kağan Yılmazer',
        technique: 'GPU-thermal-driven slime-mold simulation · live',
        description: "150,000 digital organisms deposit luminous trails that branch like fungal mycelium — Jones' (2010) Physarum sense-rotate-deposit model over a Hebbian network. Every parameter answers to the host machine's live vital signs: GPU temperature widens the sensory angle from 22° to 67°, CPU load extends sensing distance, power draw intensifies the deposits. The machine renders its own metabolic state as visible growth.",
        githubUrl: 'https://github.com/burakkagann/mycelium-metabolic-rate',
        videoSrc: '/exhibitions/animated/neural-mycelium.mp4',
        stillSrc: '/exhibitions/animated/neural-mycelium-poster.jpg',
        status: 'capture-available',
      },
      {
        id: 'selection-pressure',
        title: 'Selection Pressure',
        subtitle: 'emergent flocking',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Reynolds boid model + tournament-selection evolutionary algorithm · live',
        description: "Stars swarm under Craig Reynolds' 1987 boid rules — separation, alignment, cohesion — while black holes prowl as predators, bending light and consuming any star that drifts too close. An evolutionary algorithm runs beneath: survivors pass their behavioural weights to the next generation. The swarm learns by losing members.",
        githubUrl: 'https://github.com/burakkagann/selection-pressure',
        videoSrc: '/exhibitions/animated/selection-pressure.mp4',
        stillSrc: '/exhibitions/animated/selection-pressure-poster.jpg',
        status: 'capture-available',
      },
      {
        id: 'dissolution',
        title: 'Dissolution',
        subtitle: 'noise → portrait',
        artist: 'Burak Kağan Yılmazer',
        technique: 'DDPM forward process + ControlNet · live webcam',
        description: 'A webcam feed runs through MediaPipe face, hand, and pose tracking, Canny edges, then ControlNet-guided Stable Diffusion trained on anime. The DDPM forward process dissolves it — x_t = √(ᾱ)·image + √(1−ᾱ)·noise — until self becomes drawing, drawing becomes noise, and noise becomes self. Built from curriculum modules 12.3.2 (ControlNet) and 11.2.3 (face detection).',
        githubUrl: 'https://github.com/burakkagann/dissolution',
        status: 'capture-pending',
      },
    ],
    // Gallery clustering for the per-show #prints section. Statements are the
    // taglines from each piece's printed wall text; Maris's guest cluster stays
    // technique-free (title-only works) and links to her LinkedIn.
    printSeries: [
      {
        id: 'array-zero',
        title: 'Array Zero',
        statement: 'Creation from nothing, in four NumPy operations.',
        workIds: [
          'array-zero-void',
          'array-zero-spark',
          'array-zero-bloom',
          'array-zero-spiral-bloom',
        ],
      },
      {
        id: 'tectonic-threshold',
        title: 'Tectonic Threshold',
        statement: 'Activation functions rendered as geological landscapes.',
        workIds: ['tectonic-threshold-relu', 'tectonic-threshold-sigmoid', 'tectonic-threshold-tanh'],
      },
      {
        id: 'orbit-sediment',
        title: 'Orbit Sediment',
        statement: 'Strange attractors displaced by turbulent noise fields.',
        workIds: [
          'orbit-sediment-trichrome',
          'orbit-sediment-widespread',
          'orbit-sediment-dualglow',
        ],
      },
      {
        id: 'maris',
        title: 'Maris Nieuwenhuis',
        artist: 'Maris Nieuwenhuis',
        artistUrl: 'https://www.linkedin.com/in/maris-nieuwenhuis/',
        statement: 'Guest artist · geometry rendered in three dimensions.',
        workIds: ['maris-menger-flake', 'maris-koch-3d', 'maris-scene-rework'],
      },
    ],
    // Editorial curation for the landing § 4 plate strip — a mixed-media,
    // two-artist teaser: 3 prints (2 Burak, 1 Maris) + 2 live captures (shown
    // as still posters here; the per-show page autoplays the video).
    landingPlates: [
      'array-zero-spiral-bloom',
      'orbit-sediment-trichrome',
      'maris-menger-flake',
      'neural-mycelium',
      'selection-pressure',
    ],
  },
];

export const EXHIBITION_BY_ID: Record<string, Exhibition> = Object.fromEntries(
  EXHIBITIONS.map((e) => [e.id, e])
);

export const PAST_EXHIBITIONS = EXHIBITIONS.filter((e) => e.status === 'past');
