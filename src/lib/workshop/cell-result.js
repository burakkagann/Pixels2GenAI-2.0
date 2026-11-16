// @ts-check
/**
 * Validate a reply from the cell worker before the page shows anything.
 *
 * Learner code runs inside the worker and Pyodide lets Python post its own
 * messages to the page, so a reply is untrusted input: it may have the wrong
 * shape, lie about an image's size, or be huge. This keeps only well-formed,
 * size-capped data; the page then shows text with textContent and images from
 * raw RGBA bytes (no HTML, no image decoding of learner-made files).
 */

export const LIMITS = Object.freeze({
  stdout: 8000,
  errorLine: 500,
  errorFull: 4000,
  caption: 200,
  checkMessage: 500,
  checkLadder: 3,
  images: 12,
  side: 2048,
});

/** @param {unknown} value @param {number} max */
const str = (value, max) => (typeof value === 'string' ? value.slice(0, max) : '');
/** @param {unknown} n */
const isSide = (n) => typeof n === 'number' && Number.isInteger(n) && n >= 1 && n <= LIMITS.side;

/**
 * @typedef {object} CellImage
 * @property {number} width
 * @property {number} height
 * @property {string} caption
 * @property {Uint8ClampedArray} rgba  exactly width × height × 4 bytes
 */

/**
 * @typedef {object} CellResult
 * @property {number} id
 * @property {boolean} ok
 * @property {string} stdout
 * @property {{ kind: string, last: string, full: string } | null} error
 * @property {CellImage[]} images
 * @property {{ passed: boolean, message: string, ladder?: string[] } | null} check
 * @property {{ loadMs?: number, runMs?: number }} timings
 */

/**
 * A check's message is one string, or a list [idea, bug, line] on a failure
 * (OD-18): the list is kept as `ladder`, and `message` is its first rung.
 * @param {{ passed: boolean, message?: unknown }} check
 * @returns {{ passed: boolean, message: string, ladder?: string[] }}
 */
function readCheck({ passed, message }) {
  if (!Array.isArray(message)) return { passed, message: str(message, LIMITS.checkMessage) };
  const ladder = message.slice(0, LIMITS.checkLadder).map((rung) => str(rung, LIMITS.checkMessage));
  return { passed, message: ladder[0] ?? '', ladder };
}

/**
 * Which message a cell shows after each run of its check (OD-18): on failed
 * runs 1st the idea, 2nd the bug, 3rd and later the line. A pass starts it over.
 * So does a new idea: a step with several goals starts each goal at its idea,
 * so that getting one goal right never counts as failing the next.
 */
export function createCheckLadder() {
  let failures = 0;
  /** @type {string | undefined} */
  let idea;
  return {
    /** @param {{ passed: boolean, message: string, ladder?: string[] }} check */
    next(check) {
      if (check.passed) {
        failures = 0;
        idea = undefined;
        return check.message;
      }
      const rungs = check.ladder ?? [];
      if (rungs[0] !== idea) failures = 0;
      idea = rungs[0];
      failures += 1;
      return rungs.length ? rungs[Math.min(failures, rungs.length) - 1] : check.message;
    },
    reset() {
      failures = 0;
      idea = undefined;
    },
  };
}

/**
 * @param {unknown} data       the message from the worker
 * @param {number} expectedId  the id the page sent
 * @returns {CellResult | null} null when the reply is not a valid answer to this run
 */
export function validateCellResult(data, expectedId) {
  if (!data || typeof data !== 'object') return null;
  const d = /** @type {Record<string, any>} */ (data);
  if (d.type !== 'cell-result' || d.id !== expectedId || typeof d.ok !== 'boolean') return null;

  /** @type {CellImage[]} */
  const images = [];
  if (Array.isArray(d.images)) {
    for (const image of d.images.slice(0, LIMITS.images)) {
      if (!image || !isSide(image.width) || !isSide(image.height)) continue;
      const bytes = image.rgba;
      if (!(bytes instanceof Uint8Array) || bytes.length !== image.width * image.height * 4) continue;
      images.push({
        width: image.width,
        height: image.height,
        caption: str(image.caption, LIMITS.caption),
        rgba: new Uint8ClampedArray(bytes.buffer, bytes.byteOffset, bytes.length),
      });
    }
  }

  const error = d.error && typeof d.error === 'object'
    ? { kind: str(d.error.kind, 60) || 'Error', last: str(d.error.last, LIMITS.errorLine), full: str(d.error.full, LIMITS.errorFull) }
    : null;

  const check = d.check && typeof d.check === 'object' && typeof d.check.passed === 'boolean'
    ? readCheck(d.check)
    : null;

  /** @type {{ loadMs?: number, runMs?: number }} */
  const timings = {};
  if (d.timings && typeof d.timings === 'object') {
    for (const key of /** @type {const} */ (['loadMs', 'runMs'])) {
      if (Number.isFinite(d.timings[key]) && d.timings[key] >= 0) timings[key] = d.timings[key];
    }
  }

  let stdout = str(d.stdout, LIMITS.stdout + 40);
  if (stdout.length > LIMITS.stdout) stdout = `${stdout.slice(0, LIMITS.stdout)}\n…(output shortened)`;

  // Consistent by construction: ok means no error; not ok always carries one.
  const ok = d.ok === true && !error;
  return {
    id: expectedId,
    ok,
    stdout,
    error: ok ? null : error ?? { kind: 'Error', last: 'The code stopped with an error.', full: '' },
    images,
    check: ok ? check : null,
    timings,
  };
}
