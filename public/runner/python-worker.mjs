/**
 * Python runner (Milestone 1b): runs lesson code with Pyodide inside a module
 * Web Worker, entirely in the learner's browser. No server ever sees the code.
 *
 * Why a worker: Python can run for seconds; in a worker the page stays responsive,
 * and the page can stop a runaway script by terminating the worker.
 *
 * Message in:  { id, code, assetBase, fileName? }
 *   fileName: the script's name from the lesson (e.g. "mask.py"), used for __file__.
 *   assetBase: URL of the lesson's media folder, e.g. "/lesson-media/Module_03_.../3.2.1_mask/";
 *              files the script opens by name (bbtor.jpg, message.txt...) are fetched from there.
 * Message out: { id, ok, stdout, stderr, error, images: [{ name, mime, bytes }], timings }
 *
 * Author: Pixels2GenAI Project
 */

// Pinned version: a new Pyodide release can change package versions under the lessons.
const PYODIDE_VERSION = "314.0.7";
const PYODIDE_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

// String literals ending in these extensions may be input files the script opens.
const INPUT_FILE_PATTERN = /["']([\w\-./]+\.(?:png|jpe?g|gif|bmp|txt|csv|npy|json))["']/gi;
const OUTPUT_MIME = { png: "image/png", jpg: "image/jpeg", jpeg: "image/jpeg", gif: "image/gif" };

let pyodidePromise = null;
let runCounter = 0;

function getPyodide() {
  // Loaded once per worker; later runs reuse it (the slow part is the first load).
  if (!pyodidePromise) {
    pyodidePromise = import(`${PYODIDE_URL}pyodide.mjs`).then(({ loadPyodide }) =>
      loadPyodide({ indexURL: PYODIDE_URL }),
    );
  }
  return pyodidePromise;
}

async function copyInputFiles(pyodide, code, assetBase) {
  // We can't tell inputs from outputs by name, so try each one: a 404 just means
  // the script creates that file itself.
  const names = new Set([...code.matchAll(INPUT_FILE_PATTERN)].map((match) => match[1]));
  const copied = [];
  for (const name of names) {
    if (name.startsWith("/") || name.includes("..")) continue;   // stay inside the lesson folder
    try {
      const response = await fetch(new URL(name, new URL(assetBase, self.location.origin)));
      if (!response.ok) continue;
      const bytes = new Uint8Array(await response.arrayBuffer());
      const folder = name.includes("/") ? name.slice(0, name.lastIndexOf("/")) : "";
      if (folder) pyodide.FS.mkdirTree(folder);
      pyodide.FS.writeFile(name, bytes);
      copied.push(name);
    } catch {
      /* network error: the script will report the missing file itself */
    }
  }
  return copied;
}

function listFiles(pyodide, folder = ".") {
  // Every file under the run folder with its modification time, to spot new outputs.
  const found = new Map();
  for (const entry of pyodide.FS.readdir(folder)) {
    if (entry === "." || entry === "..") continue;
    const path = folder === "." ? entry : `${folder}/${entry}`;
    const info = pyodide.FS.stat(path);
    if (pyodide.FS.isDir(info.mode)) {
      for (const [inner, time] of listFiles(pyodide, path)) found.set(inner, time);
    } else {
      found.set(path, info.mtime.valueOf());
    }
  }
  return found;
}

self.onmessage = async ({ data }) => {
  const { id, code, assetBase, fileName } = data;
  const stdout = [];
  const stderr = [];
  const timings = {};
  const started = performance.now();
  try {
    const pyodide = await getPyodide();
    timings.loadMs = Math.round(performance.now() - started);

    // A fresh folder per run, so files from an earlier run don't show up as outputs.
    runCounter += 1;
    const runFolder = `/home/pyodide/run_${runCounter}`;
    pyodide.FS.mkdirTree(runFolder);
    pyodide.FS.chdir(runFolder);

    const packagesStarted = performance.now();
    // Installs numpy, Pillow, matplotlib, scipy, imageio... from the imports in the code.
    // Pyodide's own "Loaded numpy" messages go nowhere: the learner should see only
    // what their script prints.
    const quiet = { messageCallback: () => {} };
    await pyodide.loadPackagesFromImports(code, quiet);
    const needsFont = /truetype\(/.test(code);
    if (needsFont) await pyodide.loadPackage("matplotlib", quiet);   // ships the DejaVu Sans font
    timings.packagesMs = Math.round(performance.now() - packagesStarted);

    // Capture output only from here on, i.e. the script's own print() and warnings.
    pyodide.setStdout({ batched: (line) => stdout.push(line) });
    pyodide.setStderr({ batched: (line) => stderr.push(line) });

    const inputs = await copyInputFiles(pyodide, code, assetBase);

    // matplotlib's default browser backend needs a page; a worker has none, so use the
    // file-only Agg backend (savefig works, plt.show() does nothing).
    // Helper modules next to the script (e.g. spiral.py does `from lines import ...`):
    // fetch <name>.py from the lesson folder for every imported name; 404s are just
    // regular packages like numpy.
    const importedNames = new Set(
      [...code.matchAll(/^\s*(?:from|import)\s+([A-Za-z_]\w*)/gm)].map((match) => match[1]),
    );
    for (const name of importedNames) {
      try {
        const response = await fetch(new URL(`${name}.py`, new URL(assetBase, self.location.origin)));
        if (response.ok) pyodide.FS.writeFile(`${name}.py`, new Uint8Array(await response.arrayBuffer()));
      } catch {
        /* not a local helper */
      }
    }

    // Scripts save into subfolders that exist next to them on a learner's computer,
    // e.g. os.path.join(SCRIPT_DIR, 'visuals', 'result.png'). Create those folders:
    // every quoted literal in an os.path.join except the last (the file name).
    for (const join of code.matchAll(/os\.path\.join\(([^)]*)\)/g)) {
      const parts = [...join[1].matchAll(/["']([\w\-.]+)["']/g)].map((match) => match[1]);
      const folders = parts.slice(0, -1).filter((part) => part !== "." && part !== "..");
      if (folders.length) pyodide.FS.mkdirTree(folders.join("/"));
    }

    // The run folder goes first on the import path, and cached helper modules from an
    // earlier run are forgotten so the fresh copy is imported.
    let setup = [
      "import os, sys",
      "os.environ['MPLBACKEND'] = 'AGG'",
      "sys.path.insert(0, os.getcwd())",
      `for _name in ${JSON.stringify([...importedNames])}:`,
      "    if os.path.exists(_name + '.py'): sys.modules.pop(_name, None)",
      "",
    ].join("\n");
    if (needsFont) {
      // Four lesson scripts ask for Windows' Arial; the browser has no system fonts,
      // so put matplotlib's DejaVu Sans next to the script under the names they use.
      setup += [
        "import shutil, matplotlib",
        "_font = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf', 'DejaVuSans.ttf')",
        "for _name in ('arial.ttf', 'Arial.ttf', 'arialbd.ttf', 'DejaVuSans.ttf'):",
        "    shutil.copy(_font, _name)",
        "",
      ].join("\n");
    }
    await pyodide.runPythonAsync(setup);

    // Many lesson scripts save next to themselves with os.path.dirname(__file__), so the
    // code runs as a real file in the run folder. A fresh namespace per run means
    // variables from an earlier run can't leak into this one.
    const scriptName = /^[\w.-]+\.py$/.test(fileName || "") ? fileName : "main.py";
    pyodide.FS.writeFile(scriptName, code);
    const namespace = pyodide.toPy({ __name__: "__main__", __file__: `${runFolder}/${scriptName}` });

    const before = listFiles(pyodide);
    const runStarted = performance.now();
    try {
      await pyodide.runPythonAsync(code, { globals: namespace, filename: scriptName });
    } finally {
      namespace.destroy();
    }
    timings.runMs = Math.round(performance.now() - runStarted);

    // New or changed image files are the script's outputs.
    const images = [];
    for (const [path, modified] of listFiles(pyodide)) {
      const extension = path.split(".").pop().toLowerCase();
      if (!OUTPUT_MIME[extension] || before.get(path) === modified) continue;
      const bytes = pyodide.FS.readFile(path);
      images.push({ name: path, mime: OUTPUT_MIME[extension], bytes });
    }
    self.postMessage(
      { id, ok: true, stdout: stdout.join("\n"), stderr: stderr.join("\n"), images, inputs, timings },
      images.map((image) => image.bytes.buffer),   // hand over the bytes without copying
    );
  } catch (error) {
    // Python errors arrive as a PythonError whose message is the full traceback.
    timings.totalMs = Math.round(performance.now() - started);
    self.postMessage({
      id, ok: false, stdout: stdout.join("\n"), stderr: stderr.join("\n"),
      error: String(error && error.message ? error.message : error), images: [], timings,
    });
  }
};
