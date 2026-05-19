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
  /** One-line technique summary (mono micro-typography in card caption). */
  technique: string;
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
  status: 'capture-available' | 'capture-pending';
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
      'At the end of March 2026, the office of IT studio Academis transformed into a gallery for three days.',
    ],
    artists: [
      { name: 'Burak Kağan Yılmazer', role: 'Project author' },
      { name: 'Sara Maras' },
      { name: 'Alexander Hendorf' },
      { name: 'Hansu Kim' },
      { name: 'Maris Niewenhuis' },
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
        technique: 'NumPy · cumulative array operations · printed on paper',
        description: 'Initial state of the Array Zero series. A nearly-empty canvas under a heavy gradient field — the zero state before the bloom.',
        src: '/exhibitions/prints/array-zero-01-void.jpg',
      },
      {
        id: 'array-zero-bloom',
        title: 'Array Zero',
        subtitle: 'bloom',
        artist: 'Burak Kağan Yılmazer',
        technique: 'NumPy · radial expansion · printed on paper',
        description: 'Terminal state of the Array Zero series. The seed pixel becomes a radial bloom built from cumulative array operations.',
        src: '/exhibitions/prints/array-zero-03-bloom.jpg',
      },
      {
        id: 'fractal-square-carpet',
        title: 'Fractal Square',
        subtitle: 'carpet',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Sierpinski recursion · three-dimensional paper-cut',
        description: 'Sierpinski carpet recursion lifted into a three-dimensional paper-cut form. Six iterations of the recursion, eight folds in the paper.',
        src: '/exhibitions/prints/fractal-square-carpet.jpg',
      },
      {
        id: 'tectonic-threshold-relu',
        title: 'Tectonic Threshold',
        subtitle: 'ReLU',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Activation function plotted as terrain · printed on paper',
        description: 'The Rectified Linear Unit activation function rendered as terrain. The kink at zero becomes a geological fault running across the print.',
        src: '/exhibitions/prints/tectonic-threshold-relu.jpg',
      },
      {
        id: 'tectonic-threshold-sigmoid',
        title: 'Tectonic Threshold',
        subtitle: 'sigmoid',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Activation function plotted as terrain · printed on paper',
        description: 'The same operation under the sigmoid activation. The fault smooths into a soft ridge — the function loses its kink and the terrain heals.',
        src: '/exhibitions/prints/tectonic-threshold-sigmoid.jpg',
      },
    ],
    animatedWorks: [
      {
        id: 'neural-mycelium',
        title: 'Neural-Mycelium',
        subtitle: 'hebbian + physarum',
        artist: 'Burak Kağan Yılmazer',
        technique: 'GPU-thermal-driven slime-mold simulation · live',
        description: "Jones' (2010) Physarum sense-rotate-deposit model running over a Hebbian network, driven live by the host GPU's thermal, clock, power, and utilization metrics. The machine renders its own metabolic state as visible growth.",
        githubUrl: 'https://github.com/burakkagann/mycelium-metabolic-rate',
        stillSrc: '/exhibitions/animated/mycelium-bonded.jpg',
        hoverSrc: '/exhibitions/animated/mycelium-early.jpg',
        status: 'capture-available',
      },
      {
        id: 'selection-pressure',
        title: 'Selection Pressure',
        subtitle: 'emergent flocking',
        artist: 'Burak Kağan Yılmazer',
        technique: 'Reynolds boid model + tournament-selection evolutionary algorithm · live',
        description: "Around 800 boid stars evolve survival strategies under gravitational predation. Reynolds' 1987 boid model (separation, alignment, cohesion) coupled with an evolutionary algorithm and quorum sensing — the swarm learns by losing members.",
        githubUrl: 'https://github.com/burakkagann/selection-pressure',
        status: 'capture-pending',
      },
      {
        id: 'dissolution',
        title: 'Dissolution',
        subtitle: 'noise → portrait',
        artist: 'Burak Kağan Yılmazer',
        technique: 'DDPM forward process + ControlNet · live webcam',
        description: 'Webcam frames dissolve into Gaussian noise under the DDPM forward process and re-emerge as ControlNet-guided anime portraits. Drawn from curriculum modules 12.3.2 (ControlNet) and 11.2.3 (Face detection).',
        githubUrl: 'https://github.com/burakkagann/dissolution',
        status: 'capture-pending',
      },
    ],
    // Editorial curation for the landing § 4 plate strip.
    // 3 prints + 1 animated with still + 1 capture-pending text card.
    landingPlates: [
      'array-zero-void',
      'array-zero-bloom',
      'fractal-square-carpet',
      'neural-mycelium',
      'selection-pressure',
    ],
  },
];

export const EXHIBITION_BY_ID: Record<string, Exhibition> = Object.fromEntries(
  EXHIBITIONS.map((e) => [e.id, e])
);

export const PAST_EXHIBITIONS = EXHIBITIONS.filter((e) => e.status === 'past');
