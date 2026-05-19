// ============================================================
//  CUBE COLOR PIPELINE — Noise → OKLCH Palette LUT
//
//  Lifted verbatim from the design handoff (Björn Ottosson's
//  OKLab matrix, palette stops, and shortest-arc LUT build).
//  Approximating any of these constants will change the look.
//  Source: design_handoff_cube_color_system/README.md
// ============================================================

export type PaletteName =
  | 'riso'
  | 'aurum'
  | 'dusk'
  | 'magma'
  | 'viridis'
  | 'inferno'
  | 'plasma'
  | 'iridescent'
  | 'aurora'
  | 'twilight'
  | 'mono';

export type ColorMode = 'steady' | 'cycle' | 'drift' | 'chromatic';

type OklchStop = readonly [L: number, C: number, H: number];

interface PaletteDef {
  label: string;
  stops: readonly OklchStop[];
}

// ------------------------------------------------------------
// OKLab/OKLCH → sRGB 8-bit (Bjorn Ottosson, 2020).
// Perceptually-even palette interpolation — no muddy midpoints.
// ------------------------------------------------------------
export function oklchToSrgb(L: number, C: number, h: number): [number, number, number] {
  const hr = (h * Math.PI) / 180;
  const a = C * Math.cos(hr);
  const b = C * Math.sin(hr);

  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.2914855480 * b;
  const ll = l_ * l_ * l_;
  const mm = m_ * m_ * m_;
  const ss = s_ * s_ * s_;

  const r =  4.0767416621 * ll - 3.3077115913 * mm + 0.2309699292 * ss;
  const g = -1.2684380046 * ll + 2.6097574011 * mm - 0.3413193965 * ss;
  const bl = -0.0041960863 * ll - 0.7034186147 * mm + 1.7076147010 * ss;

  const toG = (v: number) => {
    let x = v;
    if (x < 0) x = 0;
    else if (x > 1) x = 1;
    return x <= 0.0031308 ? 12.92 * x : 1.055 * Math.pow(x, 1 / 2.4) - 0.055;
  };

  return [
    Math.round(toG(r) * 255),
    Math.round(toG(g) * 255),
    Math.round(toG(bl) * 255),
  ];
}

// ------------------------------------------------------------
// Palette stops in OKLCH: [L 0-1, Chroma ~0-0.3, Hue°]
// ------------------------------------------------------------
export const PALETTES: Record<PaletteName, PaletteDef> = {
  aurum: {
    label: 'Aurum',
    stops: [
      [0.04, 0.005, 60],
      [0.22, 0.045, 55],
      [0.50, 0.105, 70],
      [0.74, 0.135, 82],
      [0.92, 0.085, 88],
    ],
  },
  dusk: {
    label: 'Dusk',
    stops: [
      [0.07, 0.012, 290],
      [0.30, 0.075, 295],
      [0.50, 0.110, 30],
      [0.72, 0.125, 75],
      [0.94, 0.060, 88],
    ],
  },
  magma: {
    label: 'Magma',
    stops: [
      [0.01, 0.005, 300],
      [0.18, 0.095, 295],
      [0.40, 0.155, 10],
      [0.62, 0.175, 40],
      [0.84, 0.145, 75],
      [0.97, 0.045, 95],
    ],
  },
  viridis: {
    label: 'Viridis',
    stops: [
      [0.12, 0.055, 290],
      [0.32, 0.085, 235],
      [0.52, 0.105, 180],
      [0.70, 0.130, 140],
      [0.86, 0.150, 110],
      [0.96, 0.130, 95],
    ],
  },
  inferno: {
    label: 'Inferno',
    stops: [
      [0.01, 0.005, 300],
      [0.20, 0.115, 310],
      [0.44, 0.175, 20],
      [0.66, 0.180, 45],
      [0.86, 0.155, 80],
      [0.99, 0.055, 100],
    ],
  },
  plasma: {
    label: 'Plasma',
    stops: [
      [0.18, 0.115, 280],
      [0.40, 0.180, 320],
      [0.62, 0.190, 15],
      [0.82, 0.170, 65],
      [0.96, 0.170, 100],
    ],
  },
  iridescent: {
    label: 'Iridescent',
    stops: [
      [0.45, 0.130, 220],
      [0.42, 0.150, 295],
      [0.62, 0.140, 30],
      [0.70, 0.130, 85],
      [0.55, 0.135, 170],
      [0.45, 0.130, 220],
    ],
  },
  aurora: {
    label: 'Aurora',
    stops: [
      [0.14, 0.070, 230],
      [0.40, 0.140, 180],
      [0.62, 0.165, 140],
      [0.50, 0.160, 310],
      [0.30, 0.105, 285],
      [0.14, 0.070, 230],
    ],
  },
  twilight: {
    label: 'Twilight',
    stops: [
      [0.20, 0.085, 275],
      [0.45, 0.120, 320],
      [0.72, 0.080, 30],
      [0.50, 0.105, 235],
      [0.20, 0.085, 275],
    ],
  },
  mono: {
    label: 'Mono',
    stops: [
      [0.05, 0.005, 80],
      [0.40, 0.030, 78],
      [0.78, 0.030, 80],
      [0.96, 0.020, 82],
    ],
  },
  riso: {
    label: 'Riso',
    stops: [
      [0.18, 0.040, 290],  // deep violet base
      [0.50, 0.110, 135],  // lichen green
      [0.70, 0.130, 240],  // electric blue
      [0.72, 0.140, 305],  // riso violet
      [0.70, 0.145, 350],  // riso pink (L/C tuned to stay in sRGB gamut)
      [0.92, 0.040,  80],  // warm paper
      [0.18, 0.040, 290],  // loop-close for journey-palette crossfade
    ],
  },
};

// Order matters: journey-palette modifier crossfades PALETTE_ORDER[i] → PALETTE_ORDER[i+1].
export const PALETTE_ORDER: PaletteName[] = [
  'riso', 'aurum', 'dusk', 'magma', 'inferno', 'viridis',
  'plasma', 'iridescent', 'aurora', 'twilight', 'mono',
];

// ------------------------------------------------------------
// 512-entry sRGB LUT per palette, computed once.
// Hue interpolates along the shortest arc (350°→10° via 0°).
// ------------------------------------------------------------
export const LUT_SIZE = 512;
export const LUT_MAX = LUT_SIZE - 1;

export function buildLUT(stops: readonly OklchStop[]): Uint8Array {
  const N = stops.length - 1;
  const lut = new Uint8Array(LUT_SIZE * 3);
  for (let i = 0; i < LUT_SIZE; i++) {
    const u = (i / (LUT_SIZE - 1)) * N;
    let k = Math.floor(u);
    if (k >= N) k = N - 1;
    const f = u - k;
    const [L0, C0, H0] = stops[k];
    const [L1, C1, H1] = stops[k + 1];

    let dH = H1 - H0;
    if (dH > 180) dH -= 360;
    else if (dH < -180) dH += 360;

    const L = L0 + (L1 - L0) * f;
    const C = C0 + (C1 - C0) * f;
    const H = H0 + dH * f;
    const [r, g, b] = oklchToSrgb(L, C, H);
    lut[i * 3] = r;
    lut[i * 3 + 1] = g;
    lut[i * 3 + 2] = b;
  }
  return lut;
}

export const LUTS: Record<PaletteName, Uint8Array> = (() => {
  const out = {} as Record<PaletteName, Uint8Array>;
  for (const k of PALETTE_ORDER) out[k] = buildLUT(PALETTES[k].stops);
  return out;
})();

// ------------------------------------------------------------
// Cheap large-scale 2D noise (used by 'drift' mode).
// Two octaves keep it from looking like a sine grid. Range ~[0, 1].
// ------------------------------------------------------------
export function slowNoise(nx: number, ny: number, t: number): number {
  const a = Math.sin(nx * 3.1 + t * 0.28) * Math.cos(ny * 2.7 - t * 0.21);
  const b = Math.sin(nx * 6.4 - ny * 5.3 + t * 0.43);
  return 0.5 + 0.32 * a + 0.18 * b;
}
