/**
 * Pixels2GenAI workshops — recurring one-day program co-organised with
 * Academis (Kristian Rother). The pilot workshop produced the data behind
 * the /research page; future workshops will be appended here as they are
 * scheduled and run.
 */

export type WorkshopStatus = 'past' | 'upcoming' | 'planning';

export interface WorkshopModule {
  idx: string;
  title: string;
}

export interface Workshop {
  id: string;
  ordinal: string;             // "i", "ii", "iii" — Roman lowercase, matches DBR cycle register
  status: WorkshopStatus;
  date: string;                // human-readable; "TBA" for unscheduled
  dateIso?: string;            // ISO date for sort order on past workshops
  hours?: string;              // "9:00–16:00"
  city: string;
  venue?: string;
  station?: string;            // public-transport landmark, e.g. "U Kleistpark"
  participants?: number;       // realised attendance; absent for upcoming
  capacity: number;            // max participants
  fee: string;
  supervisor: string;
  supervisorHref: string;
  modules: WorkshopModule[];
  poster?: string;             // public path to poster image
  gallery?: string[];          // public paths to participant outputs
  galleryCaption?: string;
  researchLink?: boolean;      // show "Findings → /research" affordance
  outcome?: string;            // human-readable outcome line shown in the specimen dl
}

export const WORKSHOPS: Workshop[] = [
  {
    id: 'workshop-2026-02',
    ordinal: 'i',
    status: 'past',
    date: 'February 12, 2026',
    dateIso: '2026-02-12',
    hours: '9:00–16:00',
    city: 'Berlin',
    venue: 'Steinmetzstrasse 40',
    station: 'U Kleistpark',
    participants: 9,
    capacity: 8,
    fee: '10€ · drinks + snacks included',
    supervisor: 'Kristian Rother · Academis',
    supervisorHref: 'https://www.academis.eu',
    modules: [
      { idx: '1.1.1', title: 'RGB Basics' },
      { idx: '1.2.2', title: 'Cellular Automata' },
      { idx: '3.4.1', title: 'Convolution' },
      { idx: '4.1.1', title: 'Fractal Square' },
      { idx: '9.1.1', title: 'Perceptron' },
      { idx: '12.3.1', title: 'DDPM Basics' },
    ],
    poster: '/workshops/poster-2026-02.jpg',
    gallery: [
      '/workshops/gallery/fractal-01.png',
      '/workshops/gallery/fractal-02.png',
      '/workshops/gallery/fractal-03.png',
      '/workshops/gallery/fractal-04.png',
      '/workshops/gallery/fractal-05.png',
      '/workshops/gallery/fractal-06.png',
      '/workshops/gallery/fractal-07.png',
      '/workshops/gallery/fractal-08.png',
      '/workshops/gallery/fractal-09.png',
    ],
    galleryCaption:
      'Outputs from Module 4.1.1 · Fractal Square. Each participant arrived at a different self-similar pattern from the same recipe.',
    researchLink: true,
    outcome: 'Every participant improved · scores roughly tripled (3.6 → 12.1 / 24).',
  },
  // Update each 'TBA' field with the real value once the workshop is scheduled.
  // `capacity: 0` and `modules: []` are treated as TBA by the specimen component.
  {
    id: 'workshop-next',
    ordinal: 'ii',
    status: 'planning',
    date: 'TBA',
    city: 'TBA',
    capacity: 0,
    fee: 'TBA',
    supervisor: 'Kristian Rother · Academis',
    supervisorHref: 'https://www.academis.eu',
    modules: [],
  },
];

export const PAST_WORKSHOPS = WORKSHOPS.filter(w => w.status === 'past');
export const UPCOMING_WORKSHOPS = WORKSHOPS.filter(
  w => w.status === 'upcoming' || w.status === 'planning'
);
