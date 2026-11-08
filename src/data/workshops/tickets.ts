/**
 * Tickets for the series (DEC-51, DEC-55, DEC-74, DEC-75): pretix sells single tickets and the series pass
 * (5 seats per workshop), Luma sells single tickets only (3 seats). The shop links are filled in when the shops
 * go live; while a link is null its slot shows the notReady label below (not a link), so the page never shows a
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
  /** The pass for all six stops when W1 sales end (terms §1, §7); `passUntil` is the late pass. */
  passAllSixUntil: '12:00 on 4 Dec',
  passUntil: '8 Jan',
  venue: 'Academis studio, Berlin',
  /** The full venue line on /workshops (DEC-121): same studio as the pilot. `venue` above stays the short form
   *  the home series row uses. */
  venueLine: 'Academis studio · Steinmetzstraße 40, 10783 Berlin · U Kleistpark',
  /** Q-E2 (DEC-120): for now pretix sells W2–W6 only through the pass; their single tickets open later. */
  singlesLater: 'Single tickets for W2 to W6 open later. Until then the pass is the way to book them.',
  host: 'Kristian Rother',
  time: '11:00–15:30',
  terms: '/workshops/terms',
  /** The label shown in place of a ticket button while its shop link above is null. Wed 11 Nov: fill in `pretix.w1`, `pretix.pass` (and `luma.w1`) and the buttons return; this line is then unused. */
  notReady: 'Tickets open Wed 11 Nov',
  /** Open once the W1 shop link is filled in; the labels below follow it, so filling the link brings back 'On sale'. */
  get open() { return Boolean(this.pretix.w1); },
  get saleTag() { return this.open ? 'On sale' : 'Tickets Wed 11'; },
};
