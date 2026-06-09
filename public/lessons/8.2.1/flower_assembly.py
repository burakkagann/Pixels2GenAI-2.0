"""
flower_assembly.py — slice an input image into a grid of tiles, scatter the
tiles to random offscreen positions, then animate them flying back into
place. Save the result as an animated GIF.

This is the "reverse-explosion" trick: the assembly animation is the same
explosion animation played backwards, with an ease-out curve so the tiles
"settle" cleanly.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image


N_TILES = 16            # grid will be (N_TILES x N_TILES)
SOURCE = 'flower.png'
N_FRAMES = 60
SCATTER_RADIUS = 350    # how far tiles fly out
SEED = 7


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def make_input_flower(size=512):
    """Synthesize a flower-like image from polar trig if no input is given."""
    img = np.full((size, size, 3), 25, dtype=np.uint8)
    yy, xx = np.mgrid[:size, :size]
    cx, cy = size // 2, size // 2
    dy, dx = yy - cy, xx - cx
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx)
    # Rose curve r = a * cos(k*theta)
    petals = np.cos(theta * 6)
    radial = np.exp(-((r - 120 * np.abs(petals)) / 30) ** 2)
    img[..., 0] = (220 * radial).clip(0, 255).astype(np.uint8)
    img[..., 1] = (110 * radial).clip(0, 255).astype(np.uint8)
    img[..., 2] = (160 * radial).clip(0, 255).astype(np.uint8)
    # Yellow centre
    mask_centre = r < 35
    img[mask_centre] = (255, 220, 90)
    return img


def tile_centres(img, n):
    """Return per-tile (cy, cx, tile_h, tile_w) and the cropped tile arrays."""
    H, W, _ = img.shape
    th, tw = H // n, W // n
    tiles, centres = [], []
    for r in range(n):
        for c in range(n):
            y0, x0 = r * th, c * tw
            tiles.append(img[y0:y0 + th, x0:x0 + tw].copy())
            centres.append((y0, x0))
    return tiles, centres, th, tw


def render_frame(canvas_shape, tiles, centres, offsets, th, tw):
    canvas = np.full(canvas_shape, 12, dtype=np.uint8)
    for tile, (cy, cx), (dy, dx) in zip(tiles, centres, offsets):
        y = cy + dy
        x = cx + dx
        if y < 0 or x < 0 or y + th > canvas_shape[0] or x + tw > canvas_shape[1]:
            continue
        canvas[y:y + th, x:x + tw] = tile
    return canvas


def main():
    try:
        flower = np.array(Image.open(SOURCE).convert('RGB'))
    except FileNotFoundError:
        flower = make_input_flower()
        Image.fromarray(flower).save(SOURCE)

    tiles, centres, th, tw = tile_centres(flower, N_TILES)

    # Per-tile final offsets are zero. Initial offsets are random vectors
    # of length up to SCATTER_RADIUS.
    rng = np.random.default_rng(SEED)
    angles = rng.uniform(0, 2 * np.pi, len(tiles))
    radii = rng.uniform(SCATTER_RADIUS * 0.5, SCATTER_RADIUS, len(tiles))
    start_offsets = np.stack([
        (radii * np.sin(angles)).astype(int),
        (radii * np.cos(angles)).astype(int),
    ], axis=1)

    H, W, _ = flower.shape
    frames = []
    for f in range(N_FRAMES):
        t = f / (N_FRAMES - 1)
        # Tiles start scattered (t=0) and end home (t=1) with ease-out
        progress = ease_out_cubic(t)
        offsets = (start_offsets * (1 - progress)).astype(int)
        frame = render_frame(flower.shape, tiles, centres, offsets, th, tw)
        frames.append(Image.fromarray(frame))

    # Hold the assembled image for a moment
    for _ in range(15):
        frames.append(frames[-1].copy())

    frames[0].save(
        'flower_assembly.gif',
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        optimize=True,
    )
    # Single frame for the static figure
    frames[0].save('flower_scatter.png')
    frames[-1].save('flower_complete.png')
    print(f"Saved flower_assembly.gif — {N_FRAMES + 15} frames, {N_TILES**2} tiles")


if __name__ == '__main__':
    main()
