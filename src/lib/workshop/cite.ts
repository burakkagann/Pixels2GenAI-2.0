/**
 * Inline citations (CT-2, 16 Nov 2026), the runtime of <Cite> (src/components/workshop-lesson/Cite.astro).
 * - Numbers: a marker's number is the place of its reference in the lesson's Sources list (<ol data-sources>, on
 *   Wrap up), found with the same name + year match as the build check. One list, so one numbering for every screen.
 * - Card: hover (after 150 ms) or keyboard focus shows the full reference; click or Enter keeps it open. Where
 *   there is no hover, or the window is 640 px or less, it is a bottom sheet with a Close button. Escape, a click
 *   or tap outside, a scroll, a resize and a screen change close it; Escape returns the focus to the marker.
 * - The card is the next sibling of the marker's <sup>, so Tab reaches its "Open source" link; it is positioned
 *   fixed, so it is not cut off by the brief's scroll area.
 * Text goes into the DOM with textContent or cloned nodes only.
 */
import { parseCite } from '@/lib/concepts/rules.mjs';

const SHEET_QUERY = '(hover: none), (max-width: 640px)';
const HOVER_DELAY = 150;
const LEAVE_DELAY = 250;

export function startCites(root: HTMLElement) {
  const markers = [...root.querySelectorAll<HTMLButtonElement>('button[data-cite]')];
  if (!markers.length) return;
  const items = [...root.querySelectorAll<HTMLLIElement>('[data-sources] > li')];

  // ---------- numbers, names and the reference each marker opens ----------
  const itemFor = new Map<HTMLButtonElement, HTMLLIElement>();
  for (const marker of markers) {
    const parsed = parseCite(marker.dataset.cite ?? '');
    const index = parsed
      ? items.findIndex((item) => {
          const text = item.textContent ?? '';
          return text.includes(`(${parsed.year})`) && parsed.names.every((name: string) => text.includes(name));
        })
      : -1;
    if (index < 0) {
      marker.textContent = '[?]';
      continue;
    }
    itemFor.set(marker, items[index]);
    marker.dataset.n = String(index + 1);
    marker.textContent = `[${index + 1}]`;
    marker.setAttribute('aria-label', `Source ${index + 1}: ${marker.dataset.cite}`);
  }

  // ---------- the card ----------
  let card: HTMLElement | null = null;
  let active: HTMLButtonElement | null = null;
  let pinned = false;
  let timer: number | undefined;
  let counter = 0;
  let openedAt = 0;
  let quiet = false;   // true while close() hands the focus back, so that focusin does not reopen the card
  const sheetMode = () => window.matchMedia(SHEET_QUERY).matches;

  const close = (restoreFocus = false) => {
    window.clearTimeout(timer);
    const marker = active;
    const wasSheet = card?.classList.contains('wb-cite-sheet') ?? false;
    card?.remove();
    card = null;
    active = null;
    pinned = false;
    if (marker) {
      marker.setAttribute('aria-expanded', 'false');
      marker.removeAttribute('aria-describedby');
      marker.classList.remove('is-open');
      if (restoreFocus || wasSheet) {
        quiet = true;
        marker.focus({ preventScroll: true });
        quiet = false;
      }
    }
  };

  const place = (el: HTMLElement, marker: HTMLElement) => {
    const rect = marker.getBoundingClientRect();
    const width = Math.min(360, window.innerWidth - 32);
    el.style.width = `${width}px`;
    el.style.left = `${Math.max(16, Math.min(rect.left - 24, window.innerWidth - 16 - width))}px`;
    const height = el.offsetHeight;
    const below = rect.bottom + 8;
    el.style.top = `${below + height > window.innerHeight - 8 && rect.top - 8 - height > 8 ? rect.top - 8 - height : below}px`;
  };

  const open = (marker: HTMLButtonElement, asSheet: boolean) => {
    if (active === marker && card && card.classList.contains('wb-cite-sheet') === asSheet) return;
    close();
    const item = itemFor.get(marker);
    if (!item) return;
    const number = marker.dataset.n ?? '?';
    counter += 1;
    const el = document.createElement('span');
    el.className = `wb-cite-card${asSheet ? ' wb-cite-sheet' : ''}`;
    el.id = `wb-cite-card-${counter}`;

    const tag = document.createElement('span');
    tag.className = 'wb-cite-tag';
    tag.append(document.createTextNode(`Source ${number}`));
    const text = document.createElement('span');
    text.className = 'wb-cite-text';
    item.childNodes.forEach((node) => text.append(node.cloneNode(true)));
    const url = (item.textContent ?? '').match(/https?:\/\/[^\s)]+/)?.[0].replace(/[.,;]+$/, '');
    let action: HTMLElement;
    if (url) {
      const link = document.createElement('a');
      link.href = url;
      link.target = '_blank';
      link.rel = 'noopener';
      link.textContent = 'Open source ↗';
      action = link;
    } else {
      action = document.createElement('span');
      action.textContent = 'Print source, no online link';
    }
    action.classList.add('wb-cite-act');

    if (asSheet) {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'wb-cite-close';
      button.textContent = 'Close';
      button.addEventListener('click', () => close(true));
      tag.append(button);
      el.setAttribute('role', 'dialog');
      el.setAttribute('aria-label', `Source ${number}`);
    } else {
      el.setAttribute('role', 'tooltip');
      el.addEventListener('mouseenter', () => window.clearTimeout(timer));
      el.addEventListener('mouseleave', () => { if (!pinned) close(); });
    }
    el.append(tag, text, action);
    (marker.closest('sup') ?? marker).after(el);
    if (!asSheet) place(el, marker);
    marker.setAttribute('aria-expanded', 'true');
    marker.setAttribute('aria-describedby', el.id);
    marker.classList.add('is-open');
    card = el;
    active = marker;
    openedAt = performance.now();
    if (asSheet) el.querySelector<HTMLButtonElement>('.wb-cite-close')?.focus({ preventScroll: true });
  };

  const markerOf = (target: EventTarget | null): HTMLButtonElement | null =>
    target instanceof Element ? target.closest<HTMLButtonElement>('button[data-cite]') : null;
  const inRoot = (target: EventTarget | null) => target instanceof Node && root.contains(target);

  document.addEventListener('mouseover', (event) => {
    const marker = markerOf(event.target);
    if (!marker || !inRoot(marker) || sheetMode() || pinned) return;
    window.clearTimeout(timer);
    timer = window.setTimeout(() => open(marker, false), HOVER_DELAY);
  });
  document.addEventListener('mouseout', (event) => {
    const marker = markerOf(event.target);
    if (!marker || !inRoot(marker) || pinned || card?.classList.contains('wb-cite-sheet')) return;
    window.clearTimeout(timer);
    timer = window.setTimeout(() => close(), LEAVE_DELAY);
  });
  document.addEventListener('focusin', (event) => {
    const marker = markerOf(event.target);
    if (!quiet && marker && inRoot(marker) && itemFor.has(marker) && !sheetMode() && !pinned) open(marker, false);
  });
  document.addEventListener('focusout', (event) => {
    if (!card || card.classList.contains('wb-cite-sheet')) return;
    const next = event.relatedTarget as Node | null;
    // Focus moving into the card (its link) or back to the marker keeps it open; a click on blank page is the outside click.
    if (next && !card.contains(next) && next !== active) close();
    if (!next && !pinned && markerOf(event.target)) close();
  });
  root.addEventListener('click', (event) => {
    const marker = markerOf(event.target);
    if (!marker || !itemFor.has(marker)) return;
    event.preventDefault();
    event.stopPropagation();   // lesson.ts and Base.astro handle clicks too; this one is only the card
    if (sheetMode()) { open(marker, true); return; }
    if (pinned && active === marker) { close(); return; }
    open(marker, false);
    pinned = true;
  });
  document.addEventListener('click', (event) => {
    if (!card) return;
    const target = event.target as Node;
    if (card.contains(target) || (active && active.contains(target))) return;
    close();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !card) return;
    event.stopPropagation();
    close(true);
  }, true);
  // A pop is fixed to the screen, so a real scroll closes it; the scroll a focus or open causes in the first moments does not.
  window.addEventListener('scroll', () => {
    if (card && !card.classList.contains('wb-cite-sheet') && performance.now() - openedAt > 150) close();
  }, true);
  window.addEventListener('resize', () => close());
  root.addEventListener('wb:screen', () => close());
}
