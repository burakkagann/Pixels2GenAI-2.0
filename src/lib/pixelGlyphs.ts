/**
 * Pixel-glyph maps for the GitHub star CTAs — the header chip (FrameTop)
 * and the footer colophon note (Footer). Same 1x1 crispEdges <rect> idiom
 * as the octocat mark in FrameTop.astro.
 */

export interface Pixel {
  x: number;
  y: number;
}

const toPixels = (rows: string[]): Pixel[] =>
  rows.flatMap((row, y) =>
    [...row].flatMap((ch, x) => (ch === 'X' ? [{ x, y }] : [])),
  );

/** Five-point star on an 11x11 grid — render with viewBox "0 0 11 11".
 *  Pixel order is top-to-bottom, which drives the assembly stagger. */
export const STAR_PIXELS = toPixels([
  '.....X.....',
  '....XXX....',
  '....XXX....',
  'XXXXXXXXXXX',
  '.XXXXXXXXX.',
  '..XXXXXXX..',
  '...XXXXX...',
  '..XXXXXXX..',
  '..XXX.XXX..',
  '..XX...XX..',
  '.XX.....XX.',
]);

/** Four-point sparkle on a 7x7 grid — render with viewBox "0 0 7 7". */
export const SPARKLE_PIXELS = toPixels([
  '...X...',
  '...X...',
  '..XXX..',
  'XXXXXXX',
  '..XXX..',
  '...X...',
  '...X...',
]);
