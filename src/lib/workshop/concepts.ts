/**
 * Concept framework runtime (TT-A + FW-1 to FW-6, 16 Nov 2026), beside the player's lesson.ts:
 * - Check yourself and Recall questions (Predict.astro): a tap shows that option's one-sentence feedback;
 *   nothing blocks Next and nothing is stored (answers live in this page's memory only).
 * - Recall on Wrap up: the rest of Wrap up opens when every question is answered, or on "Skip".
 * - ConceptLink: "Concept: … ↩" in a step's notes panel jumps to the concept screen; there "Back to step n" returns.
 *   lesson.ts owns the stepper: this asks it for a screen with a `wb:go` event and follows `wb:screen`.
 * - ThresholdExplorer: the slider redraws the two-ink poster and the ink share.
 * New file on purpose (workshop-area has its own lesson.ts): the shared edit there is the two events only.
 * Text goes into the DOM with textContent only.
 */

export function startConcepts(root: HTMLElement, initialHash = window.location.hash) {
  const screens = [...root.querySelectorAll<HTMLElement>('.wb-screen')];
  if (!screens.length) return;
  let current = Math.max(0, screens.findIndex((screen) => !screen.hidden));
  const go = (index: number) => root.dispatchEvent(new CustomEvent('wb:go', { detail: index }));

  startQuestions(root);
  startRecall(root);
  root.querySelectorAll<HTMLElement>('[data-explore]').forEach(startExplorer);

  // ---------- concept link and "Back to step n" ----------
  let returnTo: number | null = null;
  let returnFrom: number | null = null;
  const returnButtons = screens.map((screen) => screen.querySelector<HTMLButtonElement>('[data-concept-return]'));
  const label = (screen: HTMLElement) => (screen.querySelector('.wb-kind')?.textContent ?? '').split('·')[0].trim() || (screen.dataset.title ?? 'the step');

  root.addEventListener('wb:screen', (event) => {
    current = (event as CustomEvent<number>).detail;
    // The way back shows only on the concept screen the link opened.
    if (returnFrom !== null && current !== returnFrom) {
      returnButtons[returnFrom]?.setAttribute('hidden', '');
      returnTo = null;
      returnFrom = null;
    }
  });

  const openConcept = (id: string, from: number) => {
    const target = screens.findIndex((screen) => screen.dataset.concept === id);
    if (target < 0) return false;
    go(target);
    const button = returnButtons[target];
    if (button && from !== target) {
      button.textContent = `← Back to ${label(screens[from]).toLowerCase()}`;
      button.hidden = false;
      returnTo = from;
      returnFrom = target;
      button.focus({ preventScroll: true });
    }
    return true;
  };

  root.addEventListener('click', (event) => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>('a[data-concept-link]');
    if (!link) return;
    event.preventDefault();
    event.stopPropagation();   // Base.astro's anchor handler would rewrite the hash and take the focus
    openConcept(link.dataset.conceptLink ?? '', current);
  });

  returnButtons.forEach((button) => {
    button?.addEventListener('click', () => {
      if (returnTo === null) return;
      const back = returnTo;
      go(back);
      // The link sits in the notes panel, closed after a screen change: focus it when visible, else the strip that opens the panel.
      const link = screens[back].querySelector<HTMLAnchorElement>('a[data-concept-link]');
      (link && link.offsetParent ? link : screens[back].querySelector<HTMLElement>('[data-theory-strip]') ?? link)?.focus({ preventScroll: true });
    });
  });

  // A link from elsewhere to #concept-<id> opens that screen (lesson.ts only reads #s<n>).
  const linked = initialHash.match(/^#concept-([a-z0-9-]+)$/);
  if (linked) {
    const target = screens.findIndex((screen) => screen.dataset.concept === linked[1]);
    if (target >= 0) go(target);
  }
}

/** Check yourself and Recall: each tap shows that option's feedback, "Right:" or "Not quite:". */
function startQuestions(root: HTMLElement) {
  root.querySelectorAll<HTMLElement>('[data-predict]').forEach((block) => {
    const options = [...block.querySelectorAll<HTMLButtonElement>('[data-option]')];
    const why = block.querySelector<HTMLElement>('[data-feedback]');
    const answer = block.querySelector<HTMLDetailsElement>('[data-answer]');
    if (answer) answer.hidden = true;
    options.forEach((option) => {
      option.disabled = false;
      option.addEventListener('click', () => {
        const right = option.dataset.correct === 'true';
        options.forEach((other) => other.setAttribute('aria-pressed', String(other === option)));
        block.dataset.state = right ? 'right' : 'wrong';
        block.dataset.answered = '';
        if (why) {
          why.replaceChildren();
          const verdict = document.createElement('b');
          verdict.textContent = right ? 'Right: ' : 'Not quite: ';
          why.append(verdict, document.createTextNode(option.dataset.why ?? ''));
        }
        block.dispatchEvent(new CustomEvent('wb:answered', { bubbles: true }));
      });
    });
  });
}

/** Recall first: the rest of Wrap up opens after every question has an answer, or on Skip. */
function startRecall(root: HTMLElement) {
  const block = root.querySelector<HTMLElement>('[data-recall-block]');
  if (!block) return;
  const screen = block.closest<HTMLElement>('.wb-screen');
  const rest = [...(screen?.querySelectorAll<HTMLElement>('[data-recall-rest]') ?? [])];
  const questions = [...block.querySelectorAll<HTMLElement>('[data-predict][data-recall]')];
  const skip = block.querySelector<HTMLButtonElement>('[data-recall-skip]');
  const help = screen?.querySelector<HTMLElement>('[data-help]');
  let open = false;
  const show = (value: boolean) => {
    rest.forEach((node) => { node.hidden = !value; });
    if (skip) skip.hidden = value;
  };
  show(false);
  const openRest = (focus: boolean) => {
    if (open) return;
    open = true;
    show(true);
    if (help) help.hidden = false;
    // The rest is display: contents (concepts.css), so scroll to its first element: the three lines.
    if (focus) rest[0]?.firstElementChild?.scrollIntoView({ block: 'nearest' });
  };
  block.addEventListener('wb:answered', () => {
    if (questions.every((question) => question.hasAttribute('data-answered'))) openRest(true);
  });
  skip?.addEventListener('click', () => openRest(true));
}

/** The threshold slider: poster and share for the chosen threshold. */
function startExplorer(box: HTMLElement) {
  const live = box.querySelector<HTMLElement>('[data-explore-live]');
  const still = box.querySelector<HTMLElement>('[data-explore-still]');
  const input = box.querySelector<HTMLInputElement>('[data-explore-input]');
  const canvas = box.querySelector<HTMLCanvasElement>('[data-explore-canvas]');
  const value = box.querySelector<HTMLOutputElement>('[data-explore-value]');
  const valueCopy = box.querySelector<HTMLElement>('[data-explore-value-copy]');
  const share = box.querySelector<HTMLElement>('[data-explore-share]');
  const context = canvas?.getContext('2d', { willReadFrequently: true });
  if (!live || !input || !canvas || !context || !box.dataset.image) return;
  let shares: number[] = [];
  try { shares = JSON.parse(box.dataset.shares ?? '[]'); } catch { return; }
  const rgb = (text = '') => text.split(',').map(Number);
  const ink = rgb(box.dataset.ink);
  const paper = rgb(box.dataset.paper);
  const pixelCount = share?.textContent?.match(/[\d,]+(?= pixels)/)?.[0] ?? '144,000';

  const image = new Image();
  image.decoding = 'async';
  image.addEventListener('load', () => {
    const { width, height } = canvas;
    context.drawImage(image, 0, 0, width, height);
    const grey = context.getImageData(0, 0, width, height);
    const brightness = new Uint8ClampedArray(width * height);
    for (let i = 0; i < brightness.length; i += 1) brightness[i] = grey.data[i * 4];
    const poster = context.createImageData(width, height);

    const draw = () => {
      const threshold = Number(input.value);
      for (let i = 0; i < brightness.length; i += 1) {
        const colour = brightness[i] < threshold ? ink : paper;
        poster.data[i * 4] = colour[0];
        poster.data[i * 4 + 1] = colour[1];
        poster.data[i * 4 + 2] = colour[2];
        poster.data[i * 4 + 3] = 255;
      }
      context.putImageData(poster, 0, 0);
      if (value) value.textContent = String(threshold);
      if (valueCopy) valueCopy.textContent = String(threshold);
      if (share) {
        const percent = Math.round((shares[threshold] ?? 0) * 100);
        const bold = document.createElement('b');
        bold.textContent = `${percent} %`;
        share.replaceChildren(bold, document.createTextNode(` of the ${pixelCount} pixels get ink`));
      }
    };
    input.addEventListener('input', draw);
    draw();
    live.hidden = false;
    if (still) still.hidden = true;
  });
  image.src = box.dataset.image;
}
