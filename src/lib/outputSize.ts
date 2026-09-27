/**
 * One size rule for lesson outputs, shared by the image a learner gets after
 * clicking Run (CodeBlock.astro) and the "Expected output" figure it is compared
 * with (Figure.astro inside <Dropdown summary="Expected output">). Before this,
 * the two used different rules, so a 1185 px matplotlib PNG filled the column
 * after Run while its expected figure sat at 360 px (author's request 2026-09-27).
 *
 * The script's pixel size is never changed; only how large it is shown.
 */

/** Standard display width for an output on desktop (phones get 100%). */
export const OUTPUT_WIDTH = 480;
/** Wider than this aspect ratio (side-by-sides, grids, strips) may use the full column. */
export const WIDE_ASPECT = 1.6;
/** Outputs narrower than this are small pixel art: enlarge them, crisply. */
export const SMALL_WIDTH = 240;
export const MAX_UPSCALE = 2;
/** Tall outputs never take more than this share of the screen height. */
export const TALL_VH = 60;

export interface OutputSize {
  /** Display width in CSS px before the phone (100%) and tall (60vh) limits. */
  width: number;
  /** Width / height, used for the tall limit. */
  aspect: number;
  /** True when the image is shown larger than its pixels (render crisp). */
  upscaled: boolean;
}

export function outputSize(pixelWidth: number, pixelHeight: number): OutputSize {
  const aspect = pixelWidth / pixelHeight;
  if (pixelWidth < SMALL_WIDTH) {
    return { width: Math.min(pixelWidth * MAX_UPSCALE, OUTPUT_WIDTH), aspect, upscaled: true };
  }
  if (aspect >= WIDE_ASPECT) {
    return { width: pixelWidth, aspect, upscaled: false };   // never beyond its own pixels
  }
  return { width: Math.min(pixelWidth, OUTPUT_WIDTH), aspect, upscaled: false };
}

/** Inline CSS variables read by the `.out-sized` rules in prose.css. */
export function outputSizeStyle(size: OutputSize): string {
  return `--out-w:${size.width}px;--out-ar:${size.aspect.toFixed(4)};--out-tall:${TALL_VH}vh`;
}
