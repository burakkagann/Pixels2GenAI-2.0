/**
 * The arithmetic of the pixel window (PixelWindow.astro, design B2), shared by
 * the build-time drawing and the browser script so both always agree.
 * Positions run left to right, top to bottom over the window centres that fit
 * inside the patch: (rows - 2) × (cols - 2) of them.
 */
export type KernelName = 'blur' | 'edges';

export interface PixelData {
  row0: number;
  col0: number;
  start?: number;
  values: number[][];
}

const MINUS = '−';

export const KERNELS: Record<KernelName, { weights: number[][]; label: string; cells: string[] }> = {
  blur: {
    weights: [[1, 1, 1], [1, 1, 1], [1, 1, 1]].map((row) => row.map((w) => w / 9)),
    label: 'blur, 1/9 each (sum 1)',
    cells: Array(9).fill('1/9'),
  },
  edges: {
    weights: [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]],
    label: 'edges (sum 0)',
    cells: ['-1', '-1', '-1', '-1', '8', '-1', '-1', '-1', '-1'].map((v) => v.replace('-', MINUS)),
  },
};

export function corner(data: PixelData, position: number) {
  const outCols = data.values[0].length - 2;
  return { r: Math.floor(position / outCols), c: position % outCols };
}

export function windowSum(data: PixelData, kernel: KernelName, position: number): number {
  const { r, c } = corner(data, position);
  const w = KERNELS[kernel].weights;
  let total = 0;
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) total += data.values[r + i][c + j] * w[i][j];
  return total;
}

/** One sentence: the pixel, the sum written out, the result and what it means. */
export function describe(data: PixelData, kernel: KernelName, position: number): string {
  const { r, c } = corner(data, position);
  const value = windowSum(data, kernel, position);
  const nine: number[] = [];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) nine.push(Math.round(data.values[r + i][c + j]));
  const pixel = `Pixel (${data.row0 + r + 1}, ${data.col0 + c + 1})`;
  if (kernel === 'blur') {
    const meaning = value > 120 ? 'Mostly sky: it stays bright.' : value < 60 ? 'Mostly stone: it stays dark.' : 'Half sky, half stone: in between.';
    return `${pixel}: (${nine.join(' + ')}) ÷ 9 = ${value.toFixed(1)}. ${meaning}`;
  }
  const centre = nine[4];
  const ring = nine.filter((_, i) => i !== 4);
  const meaning = Math.abs(value) < 60 ? 'The neighbours agree: close to 0, so this pixel turns black.' : 'The neighbours disagree: far from 0, an edge.';
  return `${pixel}: 8 × ${centre} ${MINUS} (${ring.join(' + ')}) = ${Math.round(value)}. ${meaning}`;
}
