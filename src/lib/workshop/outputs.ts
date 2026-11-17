/**
 * The outputs row (design B5, DEC-128): every image the learner's code drew in
 * this lesson stays visible under the cell, so earlier outputs don't vanish on
 * Next (pilot: CHAL_VISUAL_GAP; thesis T5/T6). A new run of the same screen
 * replaces that screen's images. Tapping one opens it full width, pixel-sharp,
 * with Save PNG.
 *
 * Saved in this browser only (working assumption until Kagan decides, 28 Oct):
 * a copy of each image, at most 512 px on its longer side, goes into
 * localStorage under "p2g-outputs:<lesson key>", so the row survives a reload.
 * Nothing is sent anywhere. "Clear" removes the lesson's copies. Storage can be
 * blocked or full: every access is wrapped in try/catch, the oldest screens
 * are dropped when the quota is hit, and the row still works in memory.
 * A full-size image exists only until the page is left; after a reload the
 * row shows the saved copy, and the dialog says so. Drawn from the validated
 * raw RGBA bytes (cell-result.js) or from the PNG this file saved itself;
 * text via textContent.
 */
import type { CellImage } from './cell-result.js';

interface Entry {
  screen: number;
  label: string;
  caption: string;
  canvas: HTMLCanvasElement;
  /** Which run of this screen drew it (1 = the first run this session). */
  run: number;
  /** True for the last picture of a run: the run's result. Earlier pictures are its inputs. */
  result: boolean;
  /** True when restored from storage (a copy of at most SAVED_SIDE px). */
  saved?: boolean;
}

/** One stored image in localStorage. */
interface StoredEntry {
  screen: number;
  label: string;
  caption: string;
  png: string;
  run?: number;
  result?: boolean;
}

const SAVED_SIDE = 512;
const STORE_PREFIX = 'p2g-outputs:';
const PNG_PREFIX = 'data:image/png;base64,';
const MAX_STORED = 24;              // images per lesson
const MAX_RUNS = 6;                 // results kept per screen (the first run's inputs stay)
const MAX_PNG_CHARS = 1_500_000;    // one stored image, base64 characters

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function toCanvas(image: CellImage) {
  const canvas = el('canvas');
  canvas.width = image.width;
  canvas.height = image.height;
  canvas.getContext('2d')?.putImageData(new ImageData(new Uint8ClampedArray(image.rgba), image.width, image.height), 0, 0);
  return canvas;
}

function copyCanvas(source: HTMLCanvasElement) {
  const canvas = el('canvas');
  canvas.width = source.width;
  canvas.height = source.height;
  canvas.getContext('2d')?.drawImage(source, 0, 0);
  return canvas;
}

/** A copy no larger than SAVED_SIDE on its longer side, as a PNG data URL. */
function savedCopy(source: HTMLCanvasElement) {
  const scale = Math.min(1, SAVED_SIDE / Math.max(source.width, source.height));
  const canvas = el('canvas');
  canvas.width = Math.max(1, Math.round(source.width * scale));
  canvas.height = Math.max(1, Math.round(source.height * scale));
  const context = canvas.getContext('2d');
  if (!context) return '';
  context.imageSmoothingEnabled = scale < 1;
  context.drawImage(source, 0, 0, canvas.width, canvas.height);
  try {
    return canvas.toDataURL('image/png');
  } catch {
    return '';
  }
}

function readStored(storeKey: string): StoredEntry[] {
  try {
    const raw = localStorage.getItem(storeKey);
    if (!raw) return [];
    const list: unknown = JSON.parse(raw);
    if (!Array.isArray(list)) return [];
    return list.filter((item): item is StoredEntry => (
      Boolean(item) && typeof item === 'object'
      && Number.isInteger(item.screen) && item.screen >= 0 && item.screen < 100
      && typeof item.label === 'string' && item.label.length <= 80
      && typeof item.caption === 'string' && item.caption.length <= 200
      && (item.run === undefined || (Number.isInteger(item.run) && item.run >= 1 && item.run < 1000))
      && (item.result === undefined || typeof item.result === 'boolean')
      && typeof item.png === 'string' && item.png.startsWith(PNG_PREFIX) && item.png.length <= MAX_PNG_CHARS
    )).slice(0, MAX_STORED);
  } catch {
    return [];
  }
}

/** Decode one saved PNG (made by savedCopy) into a canvas. */
function canvasFromPng(png: string) {
  return new Promise<HTMLCanvasElement | null>((resolve) => {
    const image = new Image();
    image.onload = () => {
      if (image.naturalWidth > SAVED_SIDE || image.naturalHeight > SAVED_SIDE) {
        resolve(null);
        return;
      }
      const canvas = el('canvas');
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      canvas.getContext('2d')?.drawImage(image, 0, 0);
      resolve(canvas);
    };
    image.onerror = () => resolve(null);
    image.src = png;
  });
}

const slug = (text: string) => text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'output';

/**
 * @param keepInBrowser  false on the public sample (/try): the images stay in memory for this visit only,
 *   nothing is written to localStorage, and any copy an earlier build stored is removed.
 */
export function createOutputsRow(lessonId: string, lessonKey = lessonId, keepInBrowser = true) {
  const entries: Entry[] = [];
  const storeKey = STORE_PREFIX + lessonKey;
  const pngs = new WeakMap<Entry, string>();
  const box = el('section', 'wb-outputs');
  box.setAttribute('aria-label', 'Every run this session');
  box.hidden = true;
  const head = el('div', 'wb-outputs-head');
  const title = el('span', 'wb-label');
  const saveLatest = el('button', 'wb-btn wb-btn--small', 'Save PNG ↓');
  saveLatest.type = 'button';
  saveLatest.title = 'Save the newest image as a PNG file';
  const clear = el('button', 'wb-btn wb-btn--small', 'Clear');
  clear.type = 'button';
  clear.title = 'Remove these images from the row and from this browser';
  const actions = el('span', 'wb-outputs-actions');
  actions.append(saveLatest, clear);
  head.append(title, actions);
  const row = el('ol', 'wb-outputs-row');
  box.append(head, row);

  // One dialog for the full-width view.
  const dialog = el('dialog', 'wb-outputs-dialog');
  const dialogHead = el('div', 'wb-outputs-dialog-head');
  const dialogTitle = el('span', 'wb-label');
  const dialogSave = el('button', 'wb-btn wb-btn--small', 'Save PNG ↓');
  dialogSave.type = 'button';
  const dialogClose = el('button', 'wb-btn wb-btn--small', 'Close');
  dialogClose.type = 'button';
  dialogHead.append(dialogTitle, dialogSave, dialogClose);
  const dialogBody = el('div', 'wb-outputs-dialog-body');
  const dialogNote = el('p', 'wb-outputs-note', 'A copy saved in this browser on your last visit, at most 512 pixels wide. Run the cell again for the full size.');
  dialog.append(dialogHead, dialogBody, dialogNote);
  dialogClose.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
  let open: Entry | null = null;
  let newest: Entry | null = null;

  const fileName = (entry: Entry, index: number) => `${lessonId}-${slug(entry.label)}-${slug(entry.caption)}-${index + 1}.png`;

  function save(entry: Entry) {
    const index = entries.indexOf(entry);
    entry.canvas.toBlob((blob) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = el('a');
      a.href = url;
      a.download = fileName(entry, index);
      document.body.append(a);
      a.click();
      a.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 2000);
    }, 'image/png');
  }

  function show(entry: Entry) {
    open = entry;
    dialogTitle.textContent = entry.caption ? `${entry.label} · ${entry.caption}` : entry.label;
    const big = copyCanvas(entry.canvas);
    big.setAttribute('role', 'img');
    big.setAttribute('aria-label', dialogTitle.textContent);
    dialogBody.replaceChildren(big);
    dialogNote.hidden = !entry.saved;
    if (!dialog.isConnected) document.body.append(dialog);
    dialog.showModal();
  }
  dialogSave.addEventListener('click', () => { if (open) save(open); });
  saveLatest.addEventListener('click', () => {
    if (newest && entries.includes(newest)) save(newest);
  });

  /** Write the lesson's images to this browser; drop the earliest screens when full. */
  function persist() {
    if (!keepInBrowser) return;
    const list: StoredEntry[] = entries.slice(-MAX_STORED).map((entry) => {
      let png = pngs.get(entry);
      if (png === undefined) {
        png = savedCopy(entry.canvas);
        pngs.set(entry, png);
      }
      return { screen: entry.screen, label: entry.label, caption: entry.caption, png, run: entry.run, result: entry.result };
    }).filter((item) => item.png.startsWith(PNG_PREFIX) && item.png.length <= MAX_PNG_CHARS);
    try {
      while (list.length) {
        try {
          localStorage.setItem(storeKey, JSON.stringify(list));
          return;
        } catch {
          // Quota: drop the earliest screen's images and try again.
          const first = list[0].screen;
          while (list.length && list[0].screen === first) list.shift();
        }
      }
      localStorage.removeItem(storeKey);
    } catch {
      /* storage blocked: the row still works for this visit */
    }
  }

  async function restore() {
    if (!keepInBrowser) {
      try { localStorage.removeItem(storeKey); } catch { /* storage blocked */ }
      return;
    }
    const stored = readStored(storeKey);
    for (const item of stored) {
      const canvas = await canvasFromPng(item.png);
      if (!canvas) continue;
      // A screen run in this visit before the restore finished wins.
      if (entries.some((e) => e.screen === item.screen && !e.saved)) continue;
      const entry: Entry = { screen: item.screen, label: item.label, caption: item.caption, canvas, run: item.run ?? 1, result: item.result ?? true, saved: true };
      pngs.set(entry, item.png);
      let at = entries.findIndex((e) => e.screen > item.screen);
      if (at < 0) at = entries.length;
      entries.splice(at, 0, entry);
    }
    if (!newest) newest = entries[entries.length - 1] ?? null;
    if (entries.length) render();
  }

  clear.addEventListener('click', () => {
    entries.splice(0, entries.length);
    newest = null;
    try {
      localStorage.removeItem(storeKey);
    } catch {
      /* storage blocked */
    }
    render();
  });

  function render() {
    row.replaceChildren();
    const screens = [...new Set(entries.map((e) => e.screen))];
    screens.forEach((screen) => {
      const mine = entries.filter((e) => e.screen === screen);
      const multi = mine.some((e) => e.run > 1);
      const group = el('li', 'wb-outputs-group');
      group.append(el('span', 'wb-outputs-group-name', mine[0].label));
      const thumbs = el('ol', 'wb-outputs-thumbs');
      mine.forEach((entry) => {
        const item = el('li');
        const button = el('button', 'wb-outputs-item' + (entry === newest ? ' is-new' : ''));
        button.type = 'button';
        const thumb = copyCanvas(entry.canvas);
        thumb.setAttribute('aria-hidden', 'true');
        const caption = multi && entry.result ? `run ${entry.run} · ${entry.caption}` : entry.caption;
        const text = caption ? `${entry.label} · ${caption}` : entry.label;
        button.setAttribute('aria-label', `Open ${text} full width${entry === newest ? ' (newest)' : ''}`);
        button.append(thumb, el('span', 'wb-outputs-cap', caption || entry.label));
        button.addEventListener('click', () => show(entry));
        item.append(button);
        thumbs.append(item);
      });
      group.append(thumbs);
      row.append(group);
    });
    title.textContent = `Every run this session · ${entries.length}`;
    box.hidden = entries.length === 0;
  }

  /** One picture of the run layout (a canvas copy, so the strip and the layout stay independent). */
  function figure(canvas: HTMLCanvasElement, caption: string, tag?: string, tagClass?: string) {
    const fig = el('figure', 'wb-run-fig');
    const pic = copyCanvas(canvas);
    pic.setAttribute('role', 'img');
    pic.setAttribute('aria-label', tag ? `${tag}: ${caption || 'output image'}` : caption || 'Output image');
    const cap = el('figcaption');
    if (tag) cap.append(el('span', `wb-run-tag ${tagClass ?? ''}`, tag));
    if (caption) cap.append(document.createTextNode(caption));
    fig.append(pic, cap);
    return fig;
  }

  void restore();

  return {
    element: box,
    /**
     * Keep this run in the session strip and return the layout for the output box (OL-2):
     * "Before" next to "After" for a run of one or two pictures (first run: the run's own
     * input and result; later runs: the last run's result and this one's), a plain row for
     * three or more. Null when the run drew nothing.
     */
    add(screen: number, label: string, images: CellImage[]): HTMLElement | null {
      if (!images.length) return null;
      const mine = entries.filter((e) => e.screen === screen);
      const lastRun = mine.reduce((m, e) => Math.max(m, e.run), 0);
      const before = mine.filter((e) => e.run === lastRun && e.result).pop() ?? null;
      const run = lastRun + 1;
      const canvases = images.map((image) => toCanvas(image));
      // The strip keeps the first run's pictures, then each later run's result only.
      const keep = run === 1 ? images.length : 1;
      const first = images.length - keep;
      const added: Entry[] = images.slice(first).map((image, i) => ({
        screen, label, caption: image.caption, canvas: canvases[first + i], run, result: first + i === images.length - 1,
      }));
      // Older results beyond MAX_RUNS go (the first run's inputs stay).
      const results = mine.filter((e) => e.result);
      results.slice(0, Math.max(0, results.length + 1 - MAX_RUNS)).forEach((e) => entries.splice(entries.indexOf(e), 1));
      // Keep lesson order: after the last entry of this or an earlier screen.
      let at = entries.findIndex((e) => e.screen > screen);
      if (at < 0) at = entries.length;
      entries.splice(at, 0, ...added);
      newest = added[added.length - 1];
      render();
      persist();

      const wrap = el('div', 'wb-run');
      const grid = el('div', 'wb-run-grid');
      const last = images[images.length - 1];
      let heading = '';
      if (images.length <= 2 && before) {
        heading = `Run ${run} next to run ${before.run}`;
        grid.append(
          figure(before.canvas, before.caption ? `last run: ${before.caption}` : 'last run', 'Before', 'wb-run-tag--before'),
          figure(canvases[canvases.length - 1], last.caption, 'After', 'wb-run-tag--after'),
        );
      } else if (images.length === 2) {
        heading = 'Before and after';
        grid.append(
          figure(canvases[0], images[0].caption, 'Before', 'wb-run-tag--before'),
          figure(canvases[1], last.caption, 'After', 'wb-run-tag--after'),
        );
      } else {
        grid.style.setProperty('--cols', String(images.length === 1 ? 2 : Math.min(images.length, 4)));
        grid.append(...images.map((image, i) => figure(canvases[i], image.caption)));
      }
      wrap.dataset.layout = heading ? 'pair' : 'row';
      if (heading) wrap.append(el('span', 'wb-label', heading));
      wrap.append(grid);
      return wrap;
    },
    /** Put the row under the cell of the screen in view. */
    mountIn(container: HTMLElement | null) {
      if (container && box.parentElement !== container) container.append(box);
    },
  };
}
