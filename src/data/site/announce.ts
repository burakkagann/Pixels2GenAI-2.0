import { TICKETS } from '@/data/workshops/tickets';
/**
 * Copy for the "Register interest" pop-up (AnnounceModal.astro) and its
 * no-JavaScript fallback page (/announce). Design A1a "Slip", picked by
 * Kağan on 28 Oct 2026.
 *
 * The title and lede follow the topic of the button that opened the form
 * (data-topic on the trigger, ?topic= on /announce). The workshop lines
 * mention W1 tickets only when the series is public
 * (PUBLIC_WORKSHOP_SERIES=true); otherwise the next workshop is "in
 * planning", as the classic /workshops page says.
 */

export type AnnounceTopic = 'workshops' | 'exhibitions' | 'both';

export interface AnnounceCopy {
  /** Title text before the italic part. */
  lead: string;
  /** The italic part of the title. */
  em: string;
  lede: string;
}

export const ANNOUNCE_TOPICS: AnnounceTopic[] = ['workshops', 'exhibitions', 'both'];

export function announceCopy(seriesOn: boolean): Record<AnnounceTopic, AnnounceCopy> {
  return {
    both: {
      lead: 'Hear about the ',
      em: 'next one.',
      lede: seriesOn
        ? 'One email when new workshop tickets open or a show has a date. No newsletter.'
        : 'One email when a workshop or a show has a date and a venue. No newsletter.',
    },
    workshops: {
      lead: 'Hear about the ',
      em: 'next workshop.',
      lede: seriesOn
        ? (TICKETS.open ? 'W1 tickets are on sale. ' : 'W1 tickets open soon. ') + 'We write when the next tickets open and when the showcase has a date.'
        : 'The next workshop is in planning. We write once it has a date and a venue.',
    },
    exhibitions: {
      lead: 'Hear about the ',
      em: 'next show.',
      lede: 'The next show is not scheduled yet. We write once it has a date and a venue.',
    },
  };
}

/** Shown after a successful sign-up, in the pop-up and on /announce/thanks. */
export const ANNOUNCE_DONE = {
  chip: '✓ On the list',
  title: "You're on the list.",
  text: 'We write only when there is news. Reply to any of our emails to leave the list.',
};
