"""
starwars.py — render a Star Wars-style perspective scroll: yellow text on
a starfield, projected into a trapezoid that recedes upward. The
projection uses inverse perspective sampling: for each output pixel
(x, y), compute the source pixel (x0, y0) in the unprojected text bitmap.

Pillow-only port of the OpenCV original — same geometry, no OpenCV
dependency. Output is an animated GIF.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


XSIZE, YSIZE = 720, 480
TEXT_YSIZE = 2400
PERSPECTIVE_C = 220
N_FRAMES = 120


def make_text_bitmap(filename, ysize=TEXT_YSIZE, xsize=XSIZE):
    text = open(filename).read().split('\n')
    msg = np.zeros((ysize, xsize, 3), dtype=np.uint8)
    img = Image.fromarray(msg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 28)
    except Exception:
        font = ImageFont.load_default()
    y = 60
    for line in text:
        line = line.strip()
        if not line:
            y += 28
            continue
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
        except Exception:
            w = len(line) * 14
        draw.text(((xsize - w) // 2, y), line, fill=(255, 230, 0), font=font)
        y += 42
    return np.array(img)


def make_starfield(xsize=XSIZE, ysize=YSIZE, n_stars=180, seed=11):
    rng = np.random.default_rng(seed)
    field = np.zeros((ysize, xsize, 3), dtype=np.uint8)
    ys = rng.integers(0, ysize, n_stars)
    xs = rng.integers(0, xsize, n_stars)
    brightness = rng.integers(140, 255, n_stars)
    for y, x, b in zip(ys, xs, brightness):
        field[y, x] = (b, b, b)
        if b > 220 and 1 < y < ysize - 1 and 1 < x < xsize - 1:
            field[y, x - 1] = field[y, x + 1] = (b // 2, b // 2, b // 2)
            field[y - 1, x] = field[y + 1, x] = (b // 2, b // 2, b // 2)
    return field


def prepare_perspective(c=PERSPECTIVE_C):
    """Pre-compute index arrays mapping each output row to a source row + columns."""
    indices = {}
    xx = np.arange(0, XSIZE)
    for yy in range(1, YSIZE):
        y = 1 - yy / YSIZE
        y0 = int(-y * c / (y - 1))
        x_src = (xx - XSIZE // 2 - (xx - XSIZE // 2) * y / (y - 1)).astype(int)
        x_src += XSIZE // 2
        valid = (x_src >= 0) & (x_src < XSIZE)
        indices[yy] = (y0, x_src[valid], xx[valid])
    return indices


def render_scroll():
    msg = make_text_bitmap('message.txt')
    indices = prepare_perspective()
    starfield = make_starfield()
    frames = []

    text_h = msg.shape[0]
    scroll_per_frame = (text_h - YSIZE) // N_FRAMES

    for f in range(N_FRAMES):
        frame = starfield.copy()
        ofs = f * scroll_per_frame
        for yy in range(1, YSIZE):
            y0, src_x, dst_x = indices[yy]
            src_y = ofs - y0 + text_h - YSIZE
            if 0 <= src_y < text_h:
                source_row = msg[src_y]
                pixels = source_row[src_x]
                mask = pixels.sum(axis=1) > 0
                frame[yy, dst_x[mask]] = pixels[mask]
        frames.append(Image.fromarray(frame))

    return frames


if __name__ == '__main__':
    frames = render_scroll()
    frames[0].save(
        'sw_animation.gif',
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        optimize=True,
    )
    frames[N_FRAMES // 3].save('sw_still.png')
    print(f"Saved sw_animation.gif — {N_FRAMES} frames")
