/**
 * Code cells on workshop lesson pages: run the learner's code in the cell
 * worker (public/runner/cell-worker.mjs) and show the result.
 *
 * Security rules (SEC-14, SEC-18):
 * - Learner code runs only in the worker, never on the page; Stop and the
 *   timeout end it by terminating the worker.
 * - Every worker reply is validated (cell-result.js) before use.
 * - Output is shown with textContent and images are drawn from raw RGBA bytes
 *   on a canvas. No innerHTML anywhere.
 */
import { validateCellResult, type CellResult } from './cell-result.js';
import { explainError } from './friendly-errors.js';

const RUN_TIMEOUT_MS = 120_000;   // includes the first Pyodide download

export interface RunRequest {
  code: string;
  check?: string;
  helpersUrl?: string;
  fileName?: string;
}

let worker: Worker | null = null;
let nextId = 1;
let queue: Promise<unknown> = Promise.resolve();
let stopCurrent: ((message: string) => void) | null = null;
let pythonReady = false;
const statusListeners = new Set<(ready: boolean) => void>();

export const isPythonReady = () => pythonReady;
export function onPythonStatus(listener: (ready: boolean) => void) {
  statusListeners.add(listener);
  listener(pythonReady);
}
function setReady(ready: boolean) {
  pythonReady = ready;
  statusListeners.forEach((listener) => listener(ready));
}

function getWorker(): Worker {
  if (!worker) worker = new Worker('/runner/cell-worker.mjs', { type: 'module' });
  return worker;
}

/** Start loading Python early (the first screen), so the first Run is quick. */
export function warmUp(helpersUrl?: string) {
  return runCell({ code: 'pass', helpersUrl, fileName: 'warmup.py' });
}

/** Stop the run in progress, if any. */
export function stopRun() {
  stopCurrent?.('Stopped.');
}

const failure = (id: number, last: string): CellResult => ({
  id, ok: false, stdout: '', error: { kind: 'Stopped', last, full: '' }, images: [], check: null, timings: {},
});

/** Run one cell; runs wait in a queue, one at a time (one interpreter, one output). */
export function runCell(request: RunRequest): Promise<CellResult> {
  const run = queue.then(() => start(request));
  queue = run.catch(() => undefined);
  return run;
}

function start(request: RunRequest): Promise<CellResult> {
  const id = nextId++;
  return new Promise<CellResult>((resolve) => {
    const active = getWorker();
    const finish = (result: CellResult) => {
      window.clearTimeout(timer);
      active.removeEventListener('message', onMessage);
      stopCurrent = null;
      resolve(result);
    };
    const onMessage = ({ data }: MessageEvent) => {
      const result = validateCellResult(data, id);
      if (!result) return;   // not a reply to this run (or malformed): ignore it
      if (result.error?.kind !== 'SetupError') setReady(true);
      else if (worker === active) {
        // A failed Python load is cached inside this worker; a new one lets the next run try again.
        active.terminate();
        worker = null;
      }
      finish(result);
    };
    stopCurrent = (message: string) => {
      active.terminate();
      worker = null;
      setReady(false);
      finish(failure(id, message));
    };
    const timer = window.setTimeout(() => stopCurrent?.(`Stopped after ${RUN_TIMEOUT_MS / 1000} seconds.`), RUN_TIMEOUT_MS);
    active.addEventListener('message', onMessage);
    active.postMessage({ type: 'cell', id, ...request });
  });
}

// ---------- drawing a result (DOM nodes only) ----------

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

export interface CellView {
  verdict: HTMLElement;
  output: HTMLElement;
  hasCheck: boolean;
  fileName?: string;
  /** Tag shown when the check passes (default "✓ Passed"; Make says "✓ Page ready"). */
  passLabel?: string;
}

/** The learner's line number from a traceback ("File \"step4.py\", line 11"). */
function errorLine(full: string, fileName?: string): number | null {
  if (!fileName) return null;
  const lines = [...full.matchAll(/File "([^"]+)", line (\d+)/g)].filter((m) => m[1] === fileName);
  return lines.length ? Number(lines[lines.length - 1][2]) : null;
}

/** Show a validated result: the verdict in its fixed place, then the output. */
export function showResult(view: CellView, result: CellResult) {
  const { verdict, output } = view;
  verdict.replaceChildren();
  output.replaceChildren();

  if (result.error) {
    const stopped = result.error.kind === 'Stopped';
    verdict.dataset.state = stopped ? 'idle' : 'error';
    if (stopped) {
      verdict.append(el('span', undefined, result.error.last));
    } else {
      const line = errorLine(result.error.full, view.fileName);
      const head = el('div', 'wb-verdict-head');
      head.append(el('span', 'wb-verdict-tag', line ? `Error on line ${line}` : 'Error'), el('span', 'wb-verdict-code', result.error.last));
      verdict.append(head, el('p', 'wb-verdict-text', explainError(`${result.error.kind}: ${result.error.last}`)));
      const actions = el('div', 'wb-verdict-actions');
      if (result.error.full) {
        const details = el('details', 'wb-error-full');
        details.append(el('summary', undefined, 'Full error'), el('pre', undefined, result.error.full));
        actions.append(details);
      }
      const ask = el('button', 'wb-link wb-link--tutor', '✦ Ask about this error (sends your code)');
      ask.type = 'button';
      ask.dataset.tutorError = '';
      actions.append(ask);
      verdict.append(actions);
    }
  } else if (result.check) {
    verdict.dataset.state = result.check.passed ? 'pass' : 'notyet';
    verdict.append(
      el('span', 'wb-verdict-tag', result.check.passed ? (view.passLabel ?? '✓ Passed') : 'Not yet'),
      el('span', 'wb-verdict-text', result.check.message),
    );
  } else {
    verdict.dataset.state = 'ran';
    const seconds = ((result.timings.runMs ?? 0) / 1000).toFixed(1);
    verdict.append(el('span', undefined, view.hasCheck
      ? `Ran in ${seconds} s, but the check could not run.`
      : `Ran in ${seconds} s. No check on this screen: change something and run again.`));
  }

  if (result.stdout) output.append(el('pre', 'wb-stdout', result.stdout));
  if (result.images.length) {
    const images = el('div', 'wb-images');
    for (const image of result.images) {
      const figure = el('figure', 'wb-figure');
      const canvas = el('canvas');
      canvas.width = image.width;
      canvas.height = image.height;
      canvas.setAttribute('role', 'img');
      canvas.setAttribute('aria-label', image.caption || 'Output image');
      // Copy into a plain ArrayBuffer-backed array (ImageData's type in TypeScript 5.7+).
      canvas.getContext('2d')?.putImageData(new ImageData(new Uint8ClampedArray(image.rgba), image.width, image.height), 0, 0);
      figure.append(canvas);
      if (image.caption) figure.append(el('figcaption', undefined, image.caption));
      images.append(figure);
    }
    output.append(images);
  }
  if (!result.stdout && !result.images.length) {
    output.append(el('p', 'wb-quiet', result.error ? 'Nothing yet: the code stopped before it could print or draw.' : 'Ran without output.'));
  }
}
