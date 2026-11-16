/**
 * Code-cell runner for workshop lessons (lesson framework v2, BLD-02).
 *
 * A separate worker from python-worker.mjs on purpose: the 57 live Run buttons
 * keep using that file unchanged. Both pin the same Pyodide version; the build
 * fails if they drift (src/integrations/workshop-area.mjs).
 *
 * Everything runs in the learner's browser. No code is sent anywhere.
 *
 * Message in:  { type: 'cell', id, code, check?, helpersUrl?, fileName?, photo? }
 *   photo:      { width, height, rgb: Uint8Array } the learner's own photo (writePhoto)
 *   code:       the learner's code from the editor
 *   check:      the author's check source, defining check() -> (passed, message)
 *   helpersUrl: same-origin path to the lesson's helpers.py, given by the page
 * Message out: { type: 'cell-result', id, ok, stdout, error, images, check, timings }
 *   error:  { kind, last, full } or null
 *   images: [{ width, height, caption, rgba }] from show(), raw RGBA bytes
 *   check:  { passed, message } or null (only after a run without error);
 *           message is a string, or a list [idea, bug, line] on a failed check
 *
 * The page treats every reply as untrusted (learner code can post messages too)
 * and validates it before showing anything: src/lib/workshop/cell-result.js.
 *
 * Author: Pixels2GenAI Project
 */

// Keep in step with python-worker.mjs (checked at build time).
const PYODIDE_VERSION = "314.0.7";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const MAX_IMAGES = 12;
const MAX_SIDE = 2048;
const MAX_STDOUT = 8000;

let pyodidePromise = null;
const helperCache = new Map();

function getPyodide() {
  if (!pyodidePromise) {
    pyodidePromise = import(`${PYODIDE_URL}pyodide.mjs`).then(async ({ loadPyodide }) => {
      const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
      await pyodide.loadPackage("numpy", { messageCallback: () => {} });
      return pyodide;
    });
  }
  return pyodidePromise;
}

// Helpers come only from this site (a same-origin .py path chosen by the page),
// never another origin. The path itself is supplied by the page at runtime.
async function loadHelpers(helpersUrl) {
  if (!helpersUrl) return "";
  if (!/^\/[\w\-][\w\-./]*\.py$/.test(helpersUrl) || helpersUrl.includes("..") || helpersUrl.includes("//")) {
    throw new Error("Lesson helpers must be a .py file on this site.");
  }
  if (!helperCache.has(helpersUrl)) {
    const response = await fetch(new URL(helpersUrl, self.location.origin));
    if (!response.ok) throw new Error(`Could not load the lesson helpers (${response.status}).`);
    helperCache.set(helpersUrl, await response.text());
  }
  return helperCache.get(helpersUrl);
}

// show() collects images; the worker sends them as raw RGBA bytes, so the page
// never has to decode an image format coming from learner code.
const PRELUDE = `
import numpy as np

_p2g_images = []

def show(img, caption=""):
    """Draw an image under the code: rows x columns (grey) or rows x columns x 3 (colour), values 0-255."""
    a = np.asarray(img, dtype=float)
    if a.ndim == 2:
        a = np.stack([a, a, a], axis=-1)
    if a.ndim != 3 or a.shape[2] not in (3, 4):
        raise ValueError(f"show() needs an image: rows x columns, or rows x columns x 3 colours. This one has shape {a.shape}.")
    if a.shape[0] > ${MAX_SIDE} or a.shape[1] > ${MAX_SIDE}:
        raise ValueError(f"show() draws images up to ${MAX_SIDE} x ${MAX_SIDE} pixels. This one is {a.shape[1]} x {a.shape[0]}.")
    if len(_p2g_images) >= ${MAX_IMAGES}:
        raise ValueError("show() can draw up to ${MAX_IMAGES} images per run.")
    a = np.clip(np.nan_to_num(a[..., :3]), 0, 255).astype(np.uint8)
    h, w = a.shape[:2]
    rgba = np.concatenate([a, np.full((h, w, 1), 255, np.uint8)], axis=2)
    _p2g_images.append((rgba.tobytes(), w, h, str(caption)[:200]))
`;

// The learner's own photo (BLD-14, SEC-19): optional raw RGB bytes chosen on
// the page (Make your piece, the on-ramp photo check). Written to Python's
// in-memory file system of this worker only, read by load_photo("mine") in the
// helpers, and gone when the worker ends. Never uploaded or stored.
const PHOTO_FILE = "/tmp/p2g_mine.rgb";
const PHOTO_SHAPE = "/tmp/p2g_mine.shape";

function writePhoto(pyodide, photo) {
  const valid = photo && Number.isInteger(photo.width) && Number.isInteger(photo.height)
    && photo.width > 0 && photo.height > 0 && photo.width <= MAX_SIDE && photo.height <= MAX_SIDE
    && photo.rgb instanceof Uint8Array && photo.rgb.length === photo.width * photo.height * 3;
  for (const file of [PHOTO_FILE, PHOTO_SHAPE]) {
    try { pyodide.FS.unlink(file); } catch { /* not there */ }
  }
  if (!valid) return;
  pyodide.FS.writeFile(PHOTO_FILE, photo.rgb);
  pyodide.FS.writeFile(PHOTO_SHAPE, `${photo.height} ${photo.width}`);
}

// Trim Pyodide's own frames: keep the traceback from the learner's file onwards.
function cleanTraceback(message, fileName) {
  const lines = String(message).split("\n");
  const start = lines.findIndex((line) => line.includes(`File "${fileName}"`));
  const kept = start > 0 ? ["Traceback (most recent call last):", ...lines.slice(start)] : lines;
  return kept.join("\n").trim();
}

function errorInfo(message, fileName) {
  const full = cleanTraceback(message, fileName);
  const last = full.split("\n").filter((line) => line.trim()).pop() ?? "Error";
  const kind = (last.match(/^(\w+(?:Error|Exception|Interrupt|Exit))\b/) ?? [])[1] ?? "Error";
  return { kind, last: last.slice(0, 500), full: full.slice(-4000) };
}

self.onmessage = async ({ data }) => {
  if (!data || data.type !== "cell") return;
  const { id, code, check, helpersUrl } = data;
  const fileName = /^[\w.-]+\.py$/.test(data.fileName || "") ? data.fileName : "cell.py";
  const stdout = [];
  const timings = {};
  const started = performance.now();
  let namespace = null;

  const reply = (body, transfer = []) => self.postMessage({ type: "cell-result", id, ...body, timings }, transfer);

  try {
    const pyodide = await getPyodide();
    timings.loadMs = Math.round(performance.now() - started);
    const helpers = await loadHelpers(helpersUrl);
    writePhoto(pyodide, data.photo);
    await pyodide.loadPackagesFromImports(`${helpers}\n${code}`, { messageCallback: () => {} });

    // A fresh namespace per run: cells re-create what they need, so steps work
    // in any order and nothing from an earlier run leaks in.
    namespace = pyodide.globals.get("dict")();
    namespace.set("__name__", "__main__");
    await pyodide.runPythonAsync(PRELUDE, { globals: namespace });
    if (helpers) await pyodide.runPythonAsync(helpers, { globals: namespace, filename: "helpers.py" });

    pyodide.setStdout({ batched: (line) => stdout.push(line) });
    pyodide.setStderr({ batched: (line) => stdout.push(line) });

    const runStarted = performance.now();
    let error = null;
    try {
      await pyodide.runPythonAsync(code, { globals: namespace, filename: fileName });
    } catch (err) {
      error = errorInfo(err && err.message ? err.message : err, fileName);
    }
    timings.runMs = Math.round(performance.now() - runStarted);

    // Images drawn by show(), even when the code stopped with an error later on.
    const images = [];
    const collected = namespace.get("_p2g_images");
    for (const item of collected.toJs({ create_proxies: false })) {
      const [bytes, width, height, caption] = item;
      images.push({ width, height, caption, rgba: new Uint8Array(bytes) });
    }
    collected.destroy();

    // The author's check runs only after a run without error, in the same namespace.
    let checkResult = null;
    if (!error && check) {
      try {
        await pyodide.runPythonAsync(check, { globals: namespace, filename: "check.py" });
        const result = await pyodide.runPythonAsync("check()", { globals: namespace });
        const value = result && result.toJs ? result.toJs() : result;
        if (result && result.destroy) result.destroy();
        const [passed, message] = Array.isArray(value) ? value : [false, ""];
        // A failed check may give a list [idea, bug, line]; the page picks one (OD-18).
        const text = (m) => String(m ?? "").slice(0, 500);
        checkResult = { passed: passed === true, message: Array.isArray(message) ? message.map(text) : text(message) };
      } catch {
        checkResult = { passed: false, message: "Something your code should create is missing. Read the task again." };
      }
    }

    let text = stdout.join("\n");
    if (text.length > MAX_STDOUT) text = `${text.slice(0, MAX_STDOUT)}\n…(output shortened)`;
    reply(
      { ok: !error, stdout: text, error, images, check: checkResult },
      images.map((image) => image.rgba.buffer),
    );
  } catch (err) {
    // Setup failed (Python could not load, helpers missing): not the learner's code.
    reply({
      ok: false,
      stdout: stdout.join("\n").slice(0, MAX_STDOUT),
      error: { kind: "SetupError", last: String(err && err.message ? err.message : err).slice(0, 500), full: "" },
      images: [],
      check: null,
    });
  } finally {
    if (namespace) namespace.destroy();
  }
};
