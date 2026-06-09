"""
particle_text.py — render text by spawning particles at random off-screen
positions and animating each to converge on a target pixel of the
rasterised text. Each particle has its own start position, its own
spawn delay, and a shared ease-out curve toward its home.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


CANVAS = (800, 360)
N_FRAMES = 90
N_PARTICLES = 1400
SEED = 31


def rasterise_text(text, size=160, font_size=140):
    """Render text on a small bitmap, return the (y, x) coordinates of all set pixels."""
    img = Image.new('L', (size * 5, size), 0)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', font_size)
    except Exception:
        font = ImageFont.load_default()
    draw.text((40, 0), text, fill=255, font=font)
    arr = np.array(img)
    ys, xs = np.where(arr > 0)
    return ys, xs, arr.shape


def make_particle_targets(n_particles, text='HELLO', seed=SEED):
    """Pick n_particles target positions sampled from the rasterised text."""
    rng = np.random.default_rng(seed)
    ys, xs, shape = rasterise_text(text)
    if len(ys) == 0:
        # Fallback: scatter targets in a centred rectangle
        ys = rng.integers(shape[0] // 4, 3 * shape[0] // 4, n_particles)
        xs = rng.integers(shape[1] // 4, 3 * shape[1] // 4, n_particles)
    idx = rng.integers(0, len(ys), n_particles)
    return ys[idx], xs[idx], shape


def ease_out(t):
    return 1 - (1 - t) ** 3


def main(text='HELLO', n_particles=N_PARTICLES, n_frames=N_FRAMES):
    rng = np.random.default_rng(SEED)
    target_y, target_x, raster_shape = make_particle_targets(n_particles, text)

    # Centre target positions onto the canvas
    canvas_h, canvas_w = CANVAS[1], CANVAS[0]
    txt_h, txt_w = raster_shape
    ox = (canvas_w - txt_w) // 2 + 40
    oy = (canvas_h - txt_h) // 2

    abs_target_x = target_x + ox - 40
    abs_target_y = target_y + oy

    # Spawn each particle from a random position OUTSIDE the canvas
    angles = rng.uniform(0, 2 * np.pi, n_particles)
    radii = rng.uniform(400, 900, n_particles)
    start_x = abs_target_x + (radii * np.cos(angles)).astype(int)
    start_y = abs_target_y + (radii * np.sin(angles)).astype(int)

    # Per-particle launch delay (in frames). Earliest particles arrive first.
    delays = rng.integers(0, n_frames // 2, n_particles)

    # Per-particle colour: warm gradient sampled from radius
    colors = np.zeros((n_particles, 3), dtype=np.uint8)
    norm = (radii - 400) / 500
    colors[:, 0] = (255 - norm * 50).clip(50, 255).astype(np.uint8)
    colors[:, 1] = (150 + norm * 50).clip(50, 255).astype(np.uint8)
    colors[:, 2] = (180 - norm * 80).clip(20, 255).astype(np.uint8)

    frames = []
    for f in range(n_frames):
        canvas = np.full((canvas_h, canvas_w, 3), 15, dtype=np.uint8)
        active = f >= delays
        # Each particle's local progress: max 0, (f - delay) / move_frames
        move_frames = n_frames // 2
        local = np.clip((f - delays) / move_frames, 0, 1)
        progress = ease_out(local)
        # Interpolate position
        cx = (start_x * (1 - progress) + abs_target_x * progress).astype(int)
        cy = (start_y * (1 - progress) + abs_target_y * progress).astype(int)
        # Only render in-bounds and active
        inside = (
            active
            & (cx >= 0) & (cx < canvas_w)
            & (cy >= 0) & (cy < canvas_h)
        )
        canvas[cy[inside], cx[inside]] = colors[inside]
        frames.append(Image.fromarray(canvas))

    # Hold the assembled text
    for _ in range(20):
        frames.append(frames[-1].copy())

    frames[0].save(
        'particle_text.gif',
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        optimize=True,
    )
    frames[3 * n_frames // 4].save('particle_text.png')
    print(f"Saved particle_text.gif — {n_frames + 20} frames, {n_particles} particles")


if __name__ == '__main__':
    main()
