/**
 * Workshop lesson page runtime, workbench layout (lesson page standard,
 * DEC-41; mockup: DEC-41 workbench):
 * - stepper: one screen at a time; the progress line and "3 / 9" in the
 *   lesson bar; Back / Next at the end of each brief; deep links (#s3); arrow
 *   keys outside the editor. Without JavaScript every screen stays visible.
 * - code cells: editor, Run (Ctrl+Enter), Reset; verdict in a fixed place.
 * - help: hints one level at a time (hint → … → solution), "explain it
 *   another way", and the tutor panel (not connected yet).
 * - progress for the arc page (ProgressStore): screens reached, time on the
 *   current screen, which checks passed, and "done" at Wrap up.
 * - theory on the step (TH1, TV-1): a row in the task box, opening under it in the brief
 *   beside the code; "Once it works" opens by itself when the check passes;
 *   Wrap up lists all of it, step by step.
 * - failed checks escalate (OD-18): 1st the idea, 2nd the bug, 3rd the line.
 * - design B (DEC-128): the pixel window (B2), the outputs row kept across
 *   steps (B5), and Pause on diagrams.
 * Text goes into the DOM with textContent only.
 */
import { createLocalProgressStore } from './progress.js';
import { createEditor, type CellEditor } from './editor';
import { onPythonStatus, runCell, showResult, stopRun, warmUp } from './cells';
import { createCheckLadder } from './cell-result.js';
import { createOutputsRow } from './outputs';
import { startPixelWindow } from './pixel-window';

const PHASE_ORDER = ['first', 'steps', 'yours', 'wrap'];
const popcount = (n: number) => n.toString(2).replace(/0/g, '').length;

export function startLesson(root: HTMLElement) {
  const key = root.dataset.lessonKey ?? '';
  const helpersUrl = root.dataset.helpers || undefined;
  const store = createLocalProgressStore();
  const screens = [...root.querySelectorAll<HTMLElement>('.wb-screen')];
  const checkCells = [...root.querySelectorAll<HTMLElement>('.wb-cell[data-has-check]')];
  if (!screens.length) return;
  root.classList.add('is-stepping');

  // A "___" written in the brief looks like the blank in the editor.
  root.querySelectorAll<HTMLElement>('.wb-brief code').forEach((code) => {
    if (code.textContent?.trim() === '___') code.classList.add('wb-blank');
  });

  // ---------- progress ----------
  const record = () => store.record(key);
  let mask = typeof record().checksMask === 'number' ? (record().checksMask as number) : 0;
  const passed = (cell: HTMLElement) => {
    const index = checkCells.indexOf(cell);
    return index >= 0 && Boolean(mask & (1 << index));
  };
  const allChecksPassed = () => checkCells.length === 0 || popcount(mask) >= checkCells.length;

  function markCheck(cell: HTMLElement) {
    const index = checkCells.indexOf(cell);
    if (index < 0 || index > 30) return;
    mask |= 1 << index;
    store.update(key, { checksMask: mask, checksTotal: checkCells.length, checksPassed: popcount(mask) });
  }

  // ---------- theme (the site header is hidden in focus mode) ----------
  root.querySelector<HTMLButtonElement>('[data-theme-toggle]')?.addEventListener('click', () => {
    const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('p2g-theme', next); } catch { /* storage blocked */ }
    document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
  });

  // ---------- Python status ----------
  const pill = root.querySelector<HTMLElement>('[data-py-status]');
  onPythonStatus((ready) => {
    if (!pill) return;
    pill.dataset.ready = String(ready);
    const label = pill.querySelector<HTMLElement>('[data-py-label]');
    if (label) label.textContent = ready ? 'Python ready' : 'Python loads on first run';
  });

  // ---------- outputs row (B5) ----------
  const outputs = createOutputsRow(key.split('/')[1] ?? 'lesson', key || 'lesson', !root.dataset.public);
  const screenLabel = (screen: HTMLElement | null) => {
    if (!screen) return 'Output';
    const kicker = screen.querySelector('.wb-kind')?.textContent ?? '';
    return kicker.split('·')[0].trim() || (screen.dataset.title ?? 'Output');
  };

  // ---------- cells ----------
  const runners = new Map<HTMLElement, () => Promise<void>>();
  root.querySelectorAll<HTMLElement>('.wb-cell').forEach((cell) => {
    const textarea = cell.querySelector<HTMLTextAreaElement>('[data-code]');
    const runButton = cell.querySelector<HTMLButtonElement>('[data-run]');
    const resetButton = cell.querySelector<HTMLButtonElement>('[data-reset]');
    const verdict = cell.querySelector<HTMLElement>('[data-verdict]');
    const output = cell.querySelector<HTMLElement>('[data-out]');
    if (!textarea || !runButton || !verdict || !output) return;
    const original = textarea.value;
    const idleVerdict = verdict.textContent?.trim() ?? '';
    const idleOutput = output.textContent?.trim() ?? '';
    const check = cell.querySelector<HTMLTextAreaElement>('[data-check]')?.value || undefined;
    const screen = cell.closest<HTMLElement>('.wb-screen');
    let running = false;
    const ladder = createCheckLadder();   // failed checks escalate (OD-18)
    let editor: CellEditor | null = null;

    const run = async () => {
      if (running) {
        stopRun();
        return;
      }
      running = true;
      runButton.textContent = '■ Stop';
      verdict.dataset.state = 'running';
      verdict.textContent = 'Running…';
      const firstPass = !passed(cell);
      const result = await runCell({ code: editor?.getCode() ?? textarea.value, check, helpersUrl, fileName: cell.dataset.file });
      if (result.check) result.check.message = ladder.next(result.check);
      showResult({ verdict, output, hasCheck: Boolean(check), fileName: cell.dataset.file }, result);
      if (result.check?.passed) markCheck(cell);
      if (screen) outputs.add(screens.indexOf(screen), screenLabel(screen), result.images);
      if (screen) refreshNext(screen);
      if (screen && result.check?.passed) showOnceItWorks(screen, firstPass ? verdict : null);
      if (screen && !check && !result.error) showOnceItWorks(screen, null);
      running = false;
      runButton.textContent = '▶ Run';
    };

    try {
      editor = createEditor(textarea, `Code: ${cell.dataset.file ?? 'cell'}`, run);
    } catch {
      editor = { getCode: () => textarea.value, setCode: (code) => { textarea.value = code; }, focus: () => textarea.focus() };
    }
    runners.set(cell, run);
    runButton.addEventListener('click', run);
    resetButton?.addEventListener('click', () => {
      editor?.setCode(original);
      ladder.reset();
      verdict.dataset.state = 'idle';
      verdict.textContent = idleVerdict;
      const quiet = document.createElement('p');
      quiet.className = 'wb-quiet';
      quiet.textContent = idleOutput;
      output.replaceChildren(quiet);
    });
  });

  // ---------- help: hints one level at a time, explain, tutor ----------
  const tutorClosers = new Map<HTMLElement, () => void>();
  screens.forEach((screen) => {
    const help = screen.querySelector<HTMLElement>('[data-help]');
    const items = screen.querySelector<HTMLElement>('[data-help-items]');
    if (!help || !items) return;
    const levels = [...screen.querySelectorAll<HTMLDetailsElement>('.wb-idea details.wb-hint[data-kind="hint"], .wb-idea details.wb-hint[data-kind="solution"]')];
    const explain = screen.querySelector<HTMLDetailsElement>('.wb-idea details.wb-hint[data-kind="explain"]');
    const reveal = help.querySelector<HTMLButtonElement>('[data-reveal]');
    const explainToggle = help.querySelector<HTMLButtonElement>('[data-explain-toggle]');

    // Move the hints into the help area, closed and hidden until asked for.
    for (const level of levels) {
      level.hidden = true;
      level.open = true;
      items.append(level);
    }
    if (explain) {
      explain.hidden = true;
      explain.open = true;
      items.append(explain);
    }
    let shown = 0;
    const hintCount = levels.filter((l) => l.dataset.kind === 'hint').length;
    const labelFor = (index: number) => {
      const level = levels[index];
      if (!level) return '';
      if (level.dataset.kind === 'solution') return index === 0 ? 'Show the solution' : 'Still stuck? Show the solution';
      return index === 0 ? 'Stuck? Show a hint' : `Show hint ${index + 1}`;
    };
    levels.forEach((level, index) => {
      const summary = level.querySelector('summary');
      if (summary && level.dataset.kind === 'hint' && hintCount > 1) summary.textContent = `Hint ${index + 1} of ${hintCount}`;
    });
    if (reveal && levels.length) {
      reveal.hidden = false;
      reveal.textContent = labelFor(0);
      reveal.addEventListener('click', () => {
        levels[shown].hidden = false;
        shown += 1;
        if (shown >= levels.length) reveal.hidden = true;
        else reveal.textContent = labelFor(shown);
      });
    }
    if (explainToggle && explain) {
      explainToggle.hidden = false;
      explainToggle.addEventListener('click', () => {
        explain.hidden = !explain.hidden;
        explainToggle.setAttribute('aria-expanded', String(!explain.hidden));
      });
    }
    help.hidden = false;

    // The tutor panel: opens in the brief; the idea and help step aside.
    const tutor = screen.querySelector<HTMLElement>('[data-tutor]');
    const idea = screen.querySelector<HTMLElement>('.wb-idea');
    const about = screen.querySelector<HTMLElement>('[data-tutor-about]');
    const open = (topic: string) => {
      if (!tutor) return;
      closeTheory(screen);
      if (about) about.textContent = topic;
      tutor.hidden = false;
      help.hidden = true;
      if (idea) idea.hidden = true;
      tutor.querySelector<HTMLButtonElement>('[data-tutor-close]')?.focus();
    };
    const close = () => {
      if (!tutor) return;
      tutor.hidden = true;
      help.hidden = false;
      if (idea) idea.hidden = false;
    };
    tutorClosers.set(screen, close);
    screen.querySelector('[data-tutor-open]')?.addEventListener('click', () => open('about this step'));
    screen.querySelector('[data-tutor-close]')?.addEventListener('click', close);
    screen.addEventListener('click', (event) => {
      if ((event.target as HTMLElement).closest('[data-tutor-error]')) open('about your error');
    });
  });

  // ---------- theory on the step (TH1) ----------
  // Each step shows only its own theory. It opens in the brief like the tutor:
  // the idea and help step aside, the task and the code stay in view.
  interface Theory {
    panel: HTMLElement;
    strip: HTMLButtonElement;
    after: HTMLDetailsElement | null;
  }
  const theories = new Map<HTMLElement, Theory>();
  const barHeight = () => root.querySelector('.wb-bar')?.getBoundingClientRect().height ?? 0;

  // Scrolls the page on a phone and the brief on a wide screen, clear of the sticky bar.
  const reveal = (node: HTMLElement | null) => {
    if (!node) return;
    node.style.scrollMarginTop = `${barHeight() + 12}px`;
    node.scrollIntoView({ block: 'start' });
  };

  /** Answers wait in "Once it works" until the step's check has passed. */
  const heldBack = (screen: HTMLElement) => {
    const cell = screen.querySelector<HTMLElement>('.wb-cell[data-has-check]');
    return Boolean(cell) && !passed(cell!);
  };

  // TD-1: "Once it works" stays locked until the step's check passes.
  function syncLock(screen: HTMLElement) {
    const fold = theories.get(screen)?.after;
    if (!fold) return;
    const locked = heldBack(screen);
    fold.dataset.locked = String(locked);
    if (locked) fold.open = false;
    const note = fold.querySelector<HTMLElement>('[data-lock-note]');
    if (note) note.hidden = !locked;
  }

  function openTheory(screen: HTMLElement) {
    const theory = theories.get(screen);
    if (!theory) return;
    tutorClosers.get(screen)?.();
    theory.panel.hidden = false;
    theory.strip.setAttribute('aria-expanded', 'true');
    screen.classList.add('is-theory');
  }

  function closeTheory(screen: HTMLElement) {
    const theory = theories.get(screen);
    if (!theory) return;
    theory.panel.hidden = true;
    theory.strip.setAttribute('aria-expanded', 'false');
    screen.classList.remove('is-theory');
  }

  // The first pass opens the panel; `verdict` keeps the learner's place on a
  // phone, where the panel sits above the code. A later run only opens the fold.
  function showOnceItWorks(screen: HTMLElement, verdict: HTMLElement | null) {
    const theory = theories.get(screen);
    if (!theory?.after) return;
    const before = verdict?.getBoundingClientRect().top ?? 0;
    syncLock(screen);
    buildTheoryList();
    theory.after.open = true;
    if (!verdict || screen !== screens[current]) return;
    openTheory(screen);
    window.scrollBy(0, verdict.getBoundingClientRect().top - before);
    const brief = screen.querySelector<HTMLElement>('.wb-brief-scroll');
    if (!brief) return;
    const view = brief.getBoundingClientRect();
    const fold = theory.after.getBoundingClientRect();
    if (fold.bottom > view.bottom) brief.scrollBy({ top: Math.min(fold.bottom - view.bottom, fold.top - view.top) });
  }

  screens.forEach((screen, i) => {
    const panel = screen.querySelector<HTMLElement>('[data-theory]');
    const strip = screen.querySelector<HTMLButtonElement>('[data-theory-strip]');
    if (!panel || !strip) return;
    theories.set(screen, { panel, strip, after: panel.querySelector<HTMLDetailsElement>('[data-theory-after]') });
    panel.id = `wb-theory-${i}`;
    panel.hidden = true;
    strip.hidden = false;
    strip.setAttribute('aria-controls', panel.id);
    // TV-1: the row is the last line of the task box, so theory reads as part of the job.
    const taskBox = screen.querySelector<HTMLElement>('.wb-task');
    if (taskBox) taskBox.append(strip);
    // It names the parts for this task; the answers in "Once it works" stay unnamed until the step passes.
    const names = strip.querySelector<HTMLElement>('[data-theory-names]');
    if (names) {
      const forTask = [...panel.querySelectorAll<HTMLElement>('.wb-theory-group:not([data-theory-after]) [data-part]')];
      names.textContent = forTask.map((part) => part.dataset.name).filter(Boolean).join(' · ');
    }
    const close = panel.querySelector<HTMLButtonElement>('[data-theory-close]');
    if (close) close.hidden = false;
    syncLock(screen);
    // A locked fold does not open by hand (click, Enter or Space on its summary).
    panel.querySelector<HTMLElement>('[data-theory-after] > summary')?.addEventListener('click', (event) => {
      if (heldBack(screen)) event.preventDefault();
    });
    strip.addEventListener('click', () => {
      openTheory(screen);
      close?.focus({ preventScroll: true });
      reveal(screen.querySelector<HTMLElement>('.wb-head'));
    });
    close?.addEventListener('click', () => {
      closeTheory(screen);
      strip.focus({ preventScroll: true });
    });
  });

  // A link to #theory-<id>, from the Earlier row or a hint: go to that part. A
  // fold still holding answers stays closed: the learner opens it by hand.
  root.addEventListener('click', (event) => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[href^="#theory-"]');
    if (!link) return;
    const part = root.querySelector<HTMLElement>(link.getAttribute('href') ?? '');
    const screen = part?.closest<HTMLElement>('.wb-screen');
    if (!part || !screen) return;
    event.preventDefault();
    event.stopPropagation();   // Base.astro's anchor handler would rewrite #s4 and take the focus
    if (screen !== screens[current]) go(screens.indexOf(screen));
    openTheory(screen);
    const fold = part.closest<HTMLDetailsElement>('[data-theory-after]');
    if (fold && !heldBack(screen)) fold.open = true;
    if (fold && heldBack(screen)) syncLock(screen);
    theories.get(screen)?.panel.querySelector<HTMLButtonElement>('[data-theory-close]')?.focus({ preventScroll: true });
    if (fold && !fold.open) {
      reveal(fold);
      return;
    }
    reveal(part);
    part.classList.add('is-flash');
    window.setTimeout(() => part.classList.remove('is-flash'), 1600);
  });

  // Wrap up lists every part, step by step, copied from the steps so each idea
  // is written once. The parts stay on their steps. The copies drop their ids,
  // and the line references and Go deeper links that belong beside the code.
  // TD-1: the "Once it works" parts of a step not yet passed stay out of the list;
  // it is built again when a step passes.
  function buildTheoryList() {
    const list = root.querySelector<HTMLElement>('[data-theory-all]');
    if (!list) return;
    const openNow = new Map<string, boolean>();
    list.querySelectorAll<HTMLDetailsElement>('.wb-theory-row').forEach((item) => {
      openNow.set(item.querySelector('summary b')?.textContent ?? '', item.open);
      item.remove();
    });
    const startOpen = (list.dataset.open ?? '').split(' ').filter(Boolean).map((n) => `Step ${n}`);
    const row = (label: string, parts: HTMLElement[], open: boolean) => {
      if (!parts.length) return;
      const item = document.createElement('details');
      item.className = 'wb-theory-row';
      item.open = openNow.get(label) ?? open;
      const summary = document.createElement('summary');
      const title = document.createElement('b');
      title.textContent = label;
      const names = document.createElement('span');
      const listed = parts.map((part) => part.dataset.list ?? '').filter(Boolean);
      const isPitfall = (name: string) => name.startsWith('pitfall');
      names.textContent = [...listed.filter((name) => !isPitfall(name)), ...listed.filter(isPitfall)].join(' · ');
      summary.append(title, names);
      const body = document.createElement('div');
      body.className = 'wb-theory-rowbody';
      for (const part of parts) {
        const copy = part.cloneNode(true) as HTMLElement;
        copy.removeAttribute('id');
        copy.querySelectorAll('.wb-part-line, .wb-deeper').forEach((node) => node.remove());
        body.append(copy);
      }
      item.append(summary, body);
      list.append(item);
    };
    const later: HTMLElement[] = [];
    theories.forEach(({ panel }, screen) => {
      const locked = heldBack(screen);
      const parts = [...panel.querySelectorAll<HTMLElement>('[data-part]')].filter((part) => !(locked && part.closest('[data-theory-after]')));
      later.push(...parts.filter((part) => part.dataset.wrap === 'after'));
      const label = screenLabel(screen);
      row(label, parts.filter((part) => !part.dataset.wrap), startOpen.includes(label));
    });
    row('After this lesson', later, true);
    list.hidden = false;
  }
  buildTheoryList();

  // ---------- pixel windows (B2) and diagram Pause ----------
  root.querySelectorAll<HTMLElement>('[data-pw]').forEach(startPixelWindow);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  root.querySelectorAll<HTMLElement>('[data-dg]').forEach((figure) => {
    const button = figure.querySelector<HTMLButtonElement>('[data-dg-pause]');
    const images = [...figure.querySelectorAll<HTMLImageElement>('img[data-gif][data-still]')];
    if (!button || reducedMotion || !images.length) return;
    button.hidden = false;
    let paused = false;
    button.addEventListener('click', () => {
      paused = !paused;
      images.forEach((img) => { img.src = (paused ? img.dataset.still : img.dataset.gif) ?? img.src; });
      button.textContent = paused ? '▶ Play' : '❚❚ Pause';
      button.setAttribute('aria-pressed', String(paused));
    });
  });

  // ---------- stepper ----------
  const progress = root.querySelector<HTMLElement>('[data-progress]');
  const where = root.querySelector<HTMLElement>('[data-where]');
  const segments: HTMLElement[] = [];
  if (progress) {
    let previousPhase = '';
    screens.forEach((screen, i) => {
      const phase = screen.dataset.phase ?? 'steps';
      if (previousPhase && phase !== previousPhase) {
        const gap = document.createElement('li');
        gap.className = 'wb-progress-gap';
        gap.setAttribute('aria-hidden', 'true');
        progress.append(gap);
      }
      previousPhase = phase;
      const item = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'wb-seg';
      button.dataset.phase = PHASE_ORDER.includes(phase) ? phase : 'steps';
      button.setAttribute('aria-label', `Screen ${i + 1}: ${screen.dataset.title ?? ''}`);
      button.addEventListener('click', () => go(i));
      item.append(button);
      progress.append(item);
      segments[i] = button;
    });
  }

  function refreshNext(screen: HTMLElement) {
    const cell = screen.querySelector<HTMLElement>('.wb-cell[data-has-check]');
    const next = screen.querySelector<HTMLElement>('[data-next]');
    if (next) next.dataset.ready = String(!cell || passed(cell));
  }

  let current = 0;
  function go(index: number) {
    current = Math.max(0, Math.min(screens.length - 1, index));
    screens.forEach((screen, i) => { screen.hidden = i !== current; });
    const reached = Math.max(Number(record().reached ?? 0), current + 1);
    segments.forEach((seg, i) => {
      seg.toggleAttribute('data-seen', i < reached);
      if (i === current) seg.setAttribute('aria-current', 'step');
      else seg.removeAttribute('aria-current');
    });
    if (where) where.textContent = `${current + 1} / ${screens.length}`;
    theories.forEach((theory, screen) => {
      closeTheory(screen);
      syncLock(screen);
      if (theory.after && !heldBack(screen) && screen.querySelector('.wb-cell[data-has-check]')) theory.after.open = true;
    });
    outputs.mountIn(screens[current].querySelector<HTMLElement>('.wb-bench'));
    history.replaceState(null, '', `#s${current + 1}`);
    screens[current].querySelector<HTMLElement>('.wb-brief-scroll')?.scrollTo({ top: 0 });
    window.scrollTo({ top: 0 });
    refreshNext(screens[current]);

    const now = Date.now();
    const startedAt = typeof record().startedAt === 'number' ? record().startedAt : now;
    store.update(key, { reached, total: screens.length, startedAt, screenSince: now });
    if (screens[current].dataset.phase === 'wrap') showWrap();
  }

  screens.forEach((screen, i) => {
    const nav = screen.querySelector<HTMLElement>('[data-nav]');
    if (nav) nav.hidden = false;
    const back = screen.querySelector<HTMLButtonElement>('[data-back]');
    const next = screen.querySelector<HTMLButtonElement>('[data-next]');
    if (back) {
      back.disabled = i === 0;
      back.addEventListener('click', () => go(i - 1));
    }
    if (next) {
      if (i === screens.length - 1) next.hidden = true;
      next.addEventListener('click', () => go(i + 1));
    }
  });

  // Phone bar: Back, Run (the current screen's cell), Next.
  const phoneBar = root.querySelector<HTMLElement>('[data-phonebar]');
  if (phoneBar) {
    phoneBar.hidden = false;
    phoneBar.querySelector('[data-phone-back]')?.addEventListener('click', () => go(current - 1));
    phoneBar.querySelector('[data-phone-next]')?.addEventListener('click', () => go(current + 1));
    phoneBar.querySelector('[data-phone-run]')?.addEventListener('click', async () => {
      const cell = screens[current].querySelector<HTMLElement>('.wb-cell');
      if (!cell) return;
      // From the top of the page the verdict is out of view: a failed check would
      // escalate unseen. Show it now, and again if the result has made it taller.
      const verdict = cell.querySelector<HTMLElement>('[data-verdict]');
      const underBar = () => (verdict?.getBoundingClientRect().bottom ?? 0) - phoneBar.getBoundingClientRect().top;
      const aboveView = (verdict?.getBoundingClientRect().top ?? 0) < barHeight();
      if (aboveView || underBar() > 0) verdict?.scrollIntoView({ block: 'center' });
      await runners.get(cell)?.();
      if (underBar() > 0) window.scrollBy(0, underBar() + 8);
    });
  }

  document.addEventListener('keydown', (event) => {
    const target = event.target as HTMLElement;
    if (target.closest('.cm-editor, textarea, input, select, [contenteditable]')) return;
    if (event.key === 'ArrowRight') go(current + 1);
    if (event.key === 'ArrowLeft') go(current - 1);
  });

  // ---------- wrap up: done, or what is still open ----------
  function showWrap() {
    const box = root.querySelector<HTMLElement>('[data-wrap-status]');
    if (!box) return;
    box.replaceChildren();
    const arc = root.dataset.arc ?? '/workshops/my';
    const nextLabel = root.dataset.nextLabel ?? 'the next part';
    const p = (text: string, className?: string) => {
      const node = document.createElement('p');
      if (className) node.className = className;
      node.textContent = text;
      return node;
    };
    const arcLink = () => {
      const a = document.createElement('a');
      a.className = 'wb-btn wb-btn--next';
      a.href = arc;
      a.textContent = 'Back to the arc →';
      return a;
    };

    if (allChecksPassed()) {
      store.update(key, { done: true });
      box.dataset.state = 'done';
      const text = document.createElement('div');
      // A page that is not a core (the warm-up) names its own end; a core opens the next block.
      text.append(
        p(root.dataset.doneTitle || '✓ Lesson complete', 'wb-wrap-title'),
        p(root.dataset.doneText || `${nextLabel.replace(/,$/, '')} is now open on your arc.`),
      );
      box.append(text, arcLink());
      return;
    }
    box.dataset.state = 'open';
    box.append(p('Almost there', 'wb-wrap-title'), p(root.dataset.doneText
      ? "These checks haven't passed yet:"
      : `These checks haven't passed yet. Finish them to open ${nextLabel.replace(/,$/, '')}:`));
    const list = document.createElement('ul');
    checkCells.forEach((cell, index) => {
      if (mask & (1 << index)) return;
      const screen = cell.closest<HTMLElement>('.wb-screen');
      const item = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'wb-btn wb-btn--outline';
      button.textContent = screen?.dataset.title ?? 'A step';
      button.addEventListener('click', () => go(screens.indexOf(screen!)));
      item.append(button);
      list.append(item);
    });
    box.append(list);
    const anyway = document.createElement('button');
    anyway.type = 'button';
    anyway.className = 'wb-link';
    anyway.textContent = 'Move on anyway (we note it, so we can improve the lesson)';
    anyway.addEventListener('click', () => {
      store.update(key, { anyway: true, anywayAt: Date.now() });
      window.location.href = arc;
    });
    box.append(anyway);
  }

  // Deep link: #s3 opens screen 3.
  const fromHash = Number((window.location.hash.match(/^#s(\d+)$/) ?? [])[1] ?? 1) - 1;
  // A link from another page (Make: "Where each setting comes from") lands on #theory-<id>:
  // go to that part's step and open it, as the in-page links do.
  const linked = window.location.hash.match(/^#theory-[a-z0-9-]+$/) ? root.querySelector<HTMLElement>(window.location.hash) : null;
  const linkedScreen = linked?.closest<HTMLElement>('.wb-screen') ?? null;
  go(linkedScreen ? screens.indexOf(linkedScreen) : Number.isFinite(fromHash) ? fromHash : 0);
  if (linked && linkedScreen) {
    openTheory(linkedScreen);
    const fold = linked.closest<HTMLDetailsElement>('[data-theory-after]');
    if (fold && !heldBack(linkedScreen)) fold.open = true;
    window.setTimeout(() => reveal(fold && !fold.open ? fold : linked), 150);
  }
  // PUBLIC MODE (/try): no warm-up on page load. Python and its packages come from jsDelivr, and the privacy page promises that
  // happens only after a click on Run.
  if (!root.dataset.public) warmUp(helpersUrl);
}
