// ============================================================
//  CUBE PATTERN FUNCTIONS — the eight curriculum stages
//
//  Each function returns a scalar in roughly [-1, 1].
//  Lifted verbatim from the v2c-cube-journey reference HTML.
//  These are tuned to read as their named concept; changing
//  the numeric constants will alter their visual identity.
// ============================================================

/** Off-screen canvas buffer resolution per cube face. */
export const RES = 96;

export type PatternFn = (
  nx: number,
  ny: number,
  t: number,
  ph: number,
  freq: number,
  C: number,
) => number;

export function vPixels(nx: number, ny: number, t: number, ph: number, _freq: number, _C: number): number {
  const Q = 16;
  const qx = Math.floor(nx * Q);
  const qy = Math.floor(ny * Q);
  const h = Math.sin(qx * 12.9898 + qy * 78.233 + ph + Math.floor(t * 0.4) * 0.7) * 43758.5453;
  return 2 * ((h - Math.floor(h)) - 0.5);
}

export function vRings(nx: number, ny: number, t: number, ph: number, freq: number, C: number): number {
  let acc = 0;
  for (let i = 0; i < C; i++) {
    const a = (i / C) * Math.PI * 2 + ph;
    const cx = 0.5 + Math.cos(a + t * 0.3) * 0.28;
    const cy = 0.5 + Math.sin(a * 1.3 + t * 0.22) * 0.28;
    const dx = nx - cx;
    const dy = ny - cy;
    const r = Math.sqrt(dx * dx + dy * dy) * RES;
    acc += Math.cos(r * freq + t + ph);
  }
  return acc / C;
}

export function vTransform(nx: number, ny: number, t: number, ph: number, freq: number, C: number): number {
  const cx = nx - 0.5;
  const cy = ny - 0.5;
  const ang = Math.atan2(cy, cx);
  const r = Math.sqrt(cx * cx + cy * cy) * RES;
  return Math.cos(r * freq * 0.9 + ang * (2 + (C - 3) * 0.5) + t * 0.6 + ph);
}

export function vFractal(nx: number, ny: number, t: number, ph: number, _freq: number, C: number): number {
  let x = nx;
  let y = ny;
  let v = 0;
  let scale = 1;
  const iters = Math.min(5, 2 + Math.floor(C * 0.7));
  for (let i = 0; i < iters; i++) {
    x = Math.abs(x * 2 - 1);
    y = Math.abs(y * 2 - 1);
    v += (x + y - 1) * scale;
    scale *= 0.6;
  }
  return Math.cos(v * 4 + t * 0.3 + ph);
}

export function vSimulation(nx: number, ny: number, t: number, ph: number, freq: number, _C: number): number {
  const s = freq * 8;
  return (
    Math.sin(nx * s * Math.PI + Math.cos(ny * s * Math.PI + t + ph) * 1.5) *
    Math.cos(ny * s * Math.PI - t * 0.5 + ph * 0.5)
  );
}

export function vCluster(nx: number, ny: number, t: number, ph: number, freq: number, C: number): number {
  const N = C * 2 + 2;
  let minD = 999;
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2 + ph + i * 0.41;
    const cx = 0.5 + Math.cos(a + t * 0.3) * 0.36;
    const cy = 0.5 + Math.sin(a * 1.2 + t * 0.22) * 0.36;
    const dx = nx - cx;
    const dy = ny - cy;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d < minD) minD = d;
  }
  return Math.cos(minD * RES * freq * 0.8);
}

export function vNeural(nx: number, ny: number, t: number, ph: number, _freq: number, C: number): number {
  const N = C + 3;
  let minD = 999;
  let secondD = 999;
  for (let i = 0; i < N; i++) {
    const a = (i / N) * Math.PI * 2 + ph * 0.5 + i * 0.31;
    const cx = 0.5 + Math.cos(a + t * 0.18) * 0.32;
    const cy = 0.5 + Math.sin(a * 1.4 + t * 0.13) * 0.32;
    const dx = nx - cx;
    const dy = ny - cy;
    const d = Math.sqrt(dx * dx + dy * dy);
    if (d < minD) {
      secondD = minD;
      minD = d;
    } else if (d < secondD) {
      secondD = d;
    }
  }
  const node = minD < 0.05 ? 1 : -0.6;
  const conn = minD + secondD < 0.55 ? Math.cos((minD + secondD) * 30 - t) * 0.5 : -0.4;
  return Math.max(node, conn);
}

export function vDiffusion(nx: number, ny: number, t: number, ph: number, _freq: number, _C: number): number {
  const hf = (Math.sin(nx * 47 + ny * 31 + t * 4 + ph) + Math.cos(nx * 33 + ny * 53 - t * 3 + ph)) * 0.5;
  const lf = Math.sin(nx * 6 + Math.cos(ny * 5 + t * 0.3 + ph) * 2) * Math.cos(ny * 5 + t * 0.25);
  const mix = 0.7; // mostly denoised
  return lf * mix + hf * (1 - mix) * 0.6;
}

export const STAGE_FNS: PatternFn[] = [
  vPixels,
  vRings,
  vTransform,
  vFractal,
  vSimulation,
  vCluster,
  vNeural,
  vDiffusion,
];

export interface Stage {
  code: string;
  name: string;
  desc: string;
  cycle: 'c1' | 'c2' | 'c3';
}

export const STAGES: Stage[] = [
  { code: 'M 01', name: 'Pixels',          desc: 'raw arrays, before any algorithm',                             cycle: 'c1' },
  { code: 'M 02', name: 'Distance Fields', desc: 'coordinates become rings, the first mathematical image',      cycle: 'c1' },
  { code: 'M 03', name: 'Transformations', desc: 'rotation, affine, kaleidoscope — fields become motion',       cycle: 'c1' },
  { code: 'M 04', name: 'Fractals',        desc: 'recursion: an image inside itself, again and again',          cycle: 'c1' },
  { code: 'M 05', name: 'Simulation',      desc: 'rules become particles, particles become worlds',             cycle: 'c1' },
  { code: 'M 07', name: 'Clustering',      desc: 'the first machine learning, on pixels we already know',       cycle: 'c2' },
  { code: 'M 09', name: 'Neural',          desc: 'nodes activate; the network sees what it has learned to see', cycle: 'c2' },
  { code: 'M 12', name: 'GenAI',           desc: 'from noise, a learned posterior; a model paints',             cycle: 'c3' },
];
