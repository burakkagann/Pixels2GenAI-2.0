import type { SeriesWorkshop } from '@/data/workshops/series';

/** Band → CSS key; workshops.css maps each key to a curriculum stage accent. */
export const bandKey = (band: SeriesWorkshop['band']) =>
  band === 'Foundations' ? 'foundations' : band === 'Machine learning' ? 'ml' : 'genai';

/** "2026-11-21" → "21 Nov" (the arc). Noon avoids a time-zone day shift. */
export const shortDate = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });

/** "2026-11-21" → "Saturday, 21 November 2026" (the cards). */
export const longDate = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

/** "2026-11-21" → "Sat 21 Nov 2026" (the card's date line). */
export const cardDate = (iso: string) =>
  new Date(`${iso}T12:00:00`).toLocaleDateString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).replace(',', '');
