// @ts-check
/**
 * Workshop unlock rules (DEC-28, workshop-planning/05 §2), as pure functions:
 * no browser APIs, no storage, no clock of their own. The arc page and the
 * series map call them with the learner's progress and today's date; the
 * Node test runner checks them (tests/workshop-unlock.test.mjs).
 *
 * IMPORTANT: unlocking is teaching pacing, NOT access control. It runs in the
 * browser and anyone can change their own progress to skip ahead. Nothing
 * sensitive may depend on it: who may see a workshop, use the tutor or read
 * progress is decided on the server (the edge gate and the API, SEC-10).
 */

/** Minutes on one screen before "Open the next core anyway" appears. */
export const STUCK_AFTER_MS = 10 * 60 * 1000;

/**
 * Progress of one core lesson, as kept by a ProgressStore.
 * @typedef {object} LessonProgress
 * @property {number} reached   screens reached so far (0 = not started)
 * @property {number} total     screens in the lesson
 * @property {boolean} done     reached Wrap up with every Write/Fix check passed
 * @property {boolean} anyway   the learner used "Open the next core anyway"
 * @property {number} [screenSince] when the current screen was entered (ms since epoch)
 */

/** @type {LessonProgress} */
export const NOT_STARTED = Object.freeze({ reached: 0, total: 0, done: false, anyway: false });

/**
 * Where today is relative to the workshop day. 'unscheduled' while the date
 * is TBA: an unknown date never counts as "after the day".
 * @param {string | undefined} dateIso  workshop date, "YYYY-MM-DD"
 * @param {string} todayIso             today, "YYYY-MM-DD" (local date)
 * @returns {'unscheduled' | 'before' | 'today' | 'after'}
 */
export function dayStatus(dateIso, todayIso) {
  if (!dateIso || !/^\d{4}-\d{2}-\d{2}$/.test(dateIso)) return 'unscheduled';
  if (todayIso < dateIso) return 'before';
  if (todayIso === dateIso) return 'today';
  return 'after';
}

/** A core counts as finished for unlocking when done, or skipped "anyway". */
const finished = (/** @type {LessonProgress} */ p) => p.done || p.anyway;

/**
 * @typedef {object} ArcNode
 * @property {'onramp' | 'core' | 'make' | 'show'} kind
 * @property {number} [index]      core number, 1-3
 * @property {'locked' | 'open' | 'progress' | 'done'} state
 * @property {'' | 'after-prev' | 'after-cores' | 'room' | 'review' | 'moved-on'} why  reason shown under the node
 * @property {boolean} stuck       show "Open the next core anyway"
 * @property {LessonProgress} [progress]
 */

/**
 * The arc of one workshop day: on-ramp, the cores, make your piece, show and tell.
 * @param {object} input
 * @param {LessonProgress[]} input.cores  progress of each core, in order
 * @param {number} input.roomLevel        cores the facilitator opened for the room (0 = none)
 * @param {'unscheduled' | 'before' | 'today' | 'after'} input.day
 * @param {number} input.now              current time, ms since epoch
 * @returns {ArcNode[]}
 */
export function arcNodes({ cores, roomLevel, day, now }) {
  const after = day === 'after';
  /** @type {ArcNode[]} */
  const nodes = [{ kind: 'onramp', state: 'open', why: '', stuck: false }];

  cores.forEach((progress, i) => {
    const prev = i > 0 ? cores[i - 1] : null;
    const byPrev = i === 0 || (prev !== null && finished(prev));
    const byRoom = roomLevel >= i && i > 0;
    // A core the learner has already started or finished never looks locked
    // (they may have reached it through the facilitator or a direct link).
    const begun = progress.done || progress.reached > 0;
    const open = byPrev || byRoom || after || begun;

    /** @type {ArcNode['state']} */
    let state = 'locked';
    if (open) state = progress.done ? 'done' : progress.reached > 0 ? 'progress' : 'open';

    /** @type {ArcNode['why']} */
    let why = '';
    if (!open) why = 'after-prev';
    else if (progress.anyway && !progress.done) why = 'moved-on';
    else if (!byPrev && after) why = 'review';
    else if (!byPrev && byRoom) why = 'room';

    // Only an unfinished core that is being worked on can be "stuck", and only
    // if a next step exists to open (core 3 opens "make your piece").
    const stuck = state === 'progress' && !progress.anyway
      && typeof progress.screenSince === 'number' && now - progress.screenSince >= STUCK_AFTER_MS;

    nodes.push({ kind: 'core', index: i + 1, state, why, stuck, progress });
  });

  const last = cores[cores.length - 1];
  const endOpen = (last !== undefined && finished(last)) || roomLevel >= cores.length || after;
  /** @type {ArcNode['state']} */
  const endState = endOpen ? 'open' : 'locked';
  nodes.push({ kind: 'make', state: endState, why: endOpen ? '' : 'after-cores', stuck: false });
  nodes.push({ kind: 'show', state: endState, why: endOpen ? '' : 'after-cores', stuck: false });
  return nodes;
}

/**
 * Cores finished (done or skipped) out of all, for progress segments.
 * @param {LessonProgress[]} cores
 */
export function workshopProgress(cores) {
  const done = cores.filter(finished).length;
  return { done, total: cores.length, complete: cores.length > 0 && done === cores.length };
}

/**
 * Whether this visitor may open a workshop's arc right now. Display logic
 * only: the real decision is the server's (the gate, BLD-04).
 * @param {{ scope: string, expires: string | null }} access  'all' | 'preview' | a workshop id ('w1') | 'facilitator'
 * @param {{ id: string }} workshop
 * @param {'unscheduled' | 'before' | 'today' | 'after'} day
 * @param {string} todayIso
 * @returns {'open' | 'get-ready' | 'not-in-pass' | 'expired'}  'get-ready' = a code before the day: the day page shows the Get ready state (FL-05), not a closed door
 */
export function workshopAccess(access, workshop, day, todayIso) {
  if (access.scope === 'preview') return 'open';
  if (access.expires && todayIso > access.expires) return 'expired';
  const inScope = access.scope === 'all' || access.scope === 'facilitator' || access.scope === workshop.id;
  if (!inScope) return 'not-in-pass';
  if (access.scope !== 'facilitator' && (day === 'before' || day === 'unscheduled')) return 'get-ready';
  return 'open';
}
