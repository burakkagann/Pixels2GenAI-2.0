/**
 * Tickets for the series (DEC-51, DEC-55, DEC-74, DEC-75): pretix sells single tickets and the series pass
 * (5 seats per workshop), Luma sells single tickets only (3 seats). The shop links are filled in when the shops
 * go live; while a link is null its button reads "Tickets open soon" and links nowhere, so the page never shows a
 * dead button.
 */
import type { WorkshopId } from '@/data/workshops/series';

export const TICKETS = {
  /** Workshops whose single tickets are on sale now. */
  onSale: ['w1'] as WorkshopId[],
  pretix: { w1: null, pass: null } as Record<string, string | null>,
  luma: { w1: null } as Record<string, string | null>,
  price: { standard: 90, reduced: 60, passStandard: 450, passReduced: 300 },
  /** After W1 the pass covers W2–W6 at 10% off five singles (BIZ-15). The site picks the price at build
   *  time, so it needs a redeploy on this date (BIZ-16). */
  passLate: { from: '2026-12-06', standard: 405, reduced: 270 },
  reducedFor: 'students, people on low income or unemployed',
  passUntil: '8 Jan',
  venue: 'Academis studio, Berlin',
  host: 'Kristian Rother',
  time: '11:00–15:30',
  terms: '/workshops/terms',
  notReady: 'Tickets open soon',
};
