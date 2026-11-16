/**
 * The pixel window in the browser (PixelWindow.astro, design B2): a slider and
 * Play move the 3 × 3 window; Blur / Edges switch the kernel. Text goes in with
 * textContent only. Play stops by itself when the screen is left.
 */
import { KERNELS, corner, describe, windowSum, type KernelName, type PixelData } from './pixel-window-math';

const STEP_MS = 1400;   // about one step a second and a half: slower than the v1 GIFs

export function startPixelWindow(root: HTMLElement) {
  let data: PixelData;
  try {
    data = JSON.parse(root.dataset.pixels ?? '');
  } catch {
    return;
  }
  const input = [...root.querySelectorAll<HTMLElement>('[data-pw-in] span')];
  const kernelCells = [...root.querySelectorAll<HTMLElement>('[data-pw-k] span')];
  const out = [...root.querySelectorAll<HTMLElement>('[data-pw-out] span')];
  const klabel = root.querySelector<HTMLElement>('[data-pw-klabel]');
  const sum = root.querySelector<HTMLElement>('[data-pw-sum]');
  const range = root.querySelector<HTMLInputElement>('[data-pw-range]');
  const play = root.querySelector<HTMLButtonElement>('[data-pw-play]');
  const controls = root.querySelector<HTMLElement>('[data-pw-controls]');
  const kinds = [...root.querySelectorAll<HTMLButtonElement>('[data-pw-kind]')];
  const cols = data.values[0].length;
  let kernel = (root.dataset.kernel as KernelName) ?? 'blur';
  let position = Number(root.dataset.start ?? 0);
  let timer = 0;

  const fmt = (v: number) => (kernel === 'blur' ? v.toFixed(1) : String(Math.round(v)));

  function draw() {
    const { r, c } = corner(data, position);
    input.forEach((cell, n) => {
      const i = Math.floor(n / cols);
      const j = n % cols;
      cell.classList.toggle('is-in', i >= r && i < r + 3 && j >= c && j < c + 3);
      cell.classList.toggle('is-centre', i === r + 1 && j === c + 1);
    });
    const k = KERNELS[kernel];
    kernelCells.forEach((cell, n) => { cell.textContent = k.cells[n]; });
    if (klabel) klabel.textContent = `Kernel: ${k.label}`;
    out.forEach((cell, n) => {
      cell.textContent = n <= position ? fmt(windowSum(data, kernel, n)) : '';
      cell.classList.toggle('is-done', n < position);
      cell.classList.toggle('is-now', n === position);
    });
    if (sum) sum.textContent = describe(data, kernel, position);
    if (range) range.value = String(position);
    kinds.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.pwKind === kernel)));
  }

  function stop() {
    window.clearInterval(timer);
    timer = 0;
    if (play) {
      play.textContent = '▶ Play';
      play.setAttribute('aria-pressed', 'false');
    }
  }

  range?.addEventListener('input', () => {
    stop();
    position = Number(range.value);
    draw();
  });
  play?.addEventListener('click', () => {
    if (timer) return stop();
    play.textContent = '❚❚ Pause';
    play.setAttribute('aria-pressed', 'true');
    timer = window.setInterval(() => {
      if (!root.offsetParent) return stop();   // the screen was left
      position = (position + 1) % out.length;
      draw();
    }, STEP_MS);
  });
  kinds.forEach((button) => button.addEventListener('click', () => {
    kernel = button.dataset.pwKind as KernelName;
    draw();
  }));
  if (controls) controls.hidden = false;
  draw();
}
