// @ts-check
/**
 * Workshop progress, behind one small interface (workshop-planning/05 §4).
 *
 * Today: LocalProgressStore keeps progress in this browser's localStorage.
 * Later (BLD-05): an API-backed store with the same methods, synced with this
 * one; the server copy wins.
 *
 * Privacy and security rules for anything stored here:
 * - Only the fields in LESSON_FIELDS, as numbers or booleans. No access code,
 *   no code ID, no name, no free text: every script on the origin (analytics
 *   included) can read localStorage, so it must never hold an identifier.
 * - Unlock state is pacing, not access control (see unlock.js).
 * - Storage may be blocked or full (private windows, strict settings): every
 *   read and write is wrapped, and the store falls back to memory.
 */

export const STORAGE_KEY = 'p2g-ws-progress-v1';

/** The only fields a lesson record may hold, with their type. */
const LESSON_FIELDS = /** @type {const} */ ({
  reached: 'number',
  total: 'number',
  done: 'boolean',
  anyway: 'boolean',
  anywayAt: 'number',
  startedAt: 'number',
  screenSince: 'number',
  checksPassed: 'number',
  checksTotal: 'number',
  // Which checks passed, one bit per check cell in page order (up to 31).
  checksMask: 'number',
});

/** Lesson keys look like "w1-see/3.4.1" (a workshop slug and a lesson id) or "try/print-the-berliner-dom" (the free /try lesson). */
const KEY_RE = /^(?:w[1-6]-[a-z]+\/\d+(?:\.\d+)*|try\/[a-z0-9-]+)$/;

/**
 * Keep only known fields of the right type, with sane numbers.
 * @param {Record<string, unknown>} raw
 * @returns {Record<string, number | boolean>}
 */
export function cleanLesson(raw) {
  /** @type {Record<string, number | boolean>} */
  const out = {};
  if (!raw || typeof raw !== 'object') return out;
  for (const [field, type] of Object.entries(LESSON_FIELDS)) {
    const value = raw[field];
    if (type === 'boolean' && typeof value === 'boolean') out[field] = value;
    if (type === 'number' && typeof value === 'number' && Number.isFinite(value) && value >= 0) out[field] = value;
  }
  return out;
}

/** localStorage, or null when the browser refuses it. */
function browserStorage() {
  try {
    const storage = globalThis.localStorage;
    const probe = '__p2g_probe__';
    storage.setItem(probe, '1');
    storage.removeItem(probe);
    return storage;
  } catch {
    return null;
  }
}

/**
 * @typedef {object} ProgressStore
 * @property {(key: string) => import('./unlock.js').LessonProgress} lesson
 * @property {(key: string) => Record<string, number | boolean>} record  every stored field of one lesson
 * @property {(key: string, patch: Record<string, unknown>) => void} update
 * @property {(workshopSlug: string) => number} roomLevel  cores the facilitator opened (BLD-06; 0 locally)
 */

/**
 * @param {Pick<Storage, 'getItem' | 'setItem'> | null} [storage]  injectable for tests
 * @returns {ProgressStore}
 */
export function createLocalProgressStore(storage = browserStorage()) {
  /** @type {Record<string, Record<string, number | boolean>>} */
  let memory = {};

  const read = () => {
    if (!storage) return memory;
    try {
      const parsed = JSON.parse(storage.getItem(STORAGE_KEY) ?? '{}');
      const lessons = parsed && parsed.v === 1 && parsed.lessons && typeof parsed.lessons === 'object' ? parsed.lessons : {};
      /** @type {Record<string, Record<string, number | boolean>>} */
      const clean = {};
      for (const [key, value] of Object.entries(lessons)) {
        if (KEY_RE.test(key)) clean[key] = cleanLesson(/** @type {Record<string, unknown>} */ (value));
      }
      return clean;
    } catch {
      return {};
    }
  };

  const write = (/** @type {Record<string, Record<string, number | boolean>>} */ lessons) => {
    memory = lessons;
    if (!storage) return;
    try {
      storage.setItem(STORAGE_KEY, JSON.stringify({ v: 1, lessons }));
    } catch {
      /* storage full or blocked: keep the in-memory copy for this page */
    }
  };

  return {
    lesson(key) {
      const record = read()[key] ?? {};
      return {
        reached: typeof record.reached === 'number' ? record.reached : 0,
        total: typeof record.total === 'number' ? record.total : 0,
        done: record.done === true,
        anyway: record.anyway === true,
        ...(typeof record.screenSince === 'number' ? { screenSince: record.screenSince } : {}),
      };
    },
    record(key) {
      return { ...(read()[key] ?? {}) };
    },
    update(key, patch) {
      if (!KEY_RE.test(key)) return;
      const lessons = read();
      lessons[key] = cleanLesson({ ...lessons[key], ...cleanLesson(patch) });
      write(lessons);
    },
    roomLevel() {
      return 0;
    },
  };
}
