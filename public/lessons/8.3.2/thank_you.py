"""
thank_you.py — Pillow-only port of the original OpenCV demo: two
characters (panda + pingu) slide in from the left and right edges,
a speech bubble fades in between them, and a "Thank You" text rises
from below into the bubble.

All four sub-animations are driven by sinusoidal ease-out moves on
disjoint timelines, illustrating how independent staggered tweens
compose into a single sequence.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont


MAXX, MAXY = 1800, 720
N_FRAMES = 140
YCHARS = 280


def sine_move(start, end, frames, wait_frames=0):
    """Smooth ease-out move from start to end over `frames` frames, then hold."""
    seq = []
    for _ in range(wait_frames):
        seq.append(start)
    for i in range(frames):
        angle = i / frames * math.pi / 2
        eased = math.sin(angle)
        seq.append(int(start + (end - start) * eased))
    return seq


def create_text(text='Thank You', size=(360, 100), color=(60, 70, 100)):
    """Render the text onto a white tile."""
    img = Image.new('RGB', size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('arial.ttf', 56)
    except Exception:
        font = ImageFont.load_default()
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        tw, th = len(text) * 24, 56
    draw.text(((size[0] - tw) // 2, (size[1] - th) // 2 - 5),
              text, fill=color, font=font)
    return img


def safe_load(name, fallback_size, fallback_color):
    try:
        return Image.open(name).convert('RGBA').resize(fallback_size)
    except FileNotFoundError:
        img = Image.new('RGBA', fallback_size, fallback_color + (255,))
        return img


def main():
    panda = safe_load('panda.png', (260, 260), (120, 220, 255))
    pingu = safe_load('pingu.png', (260, 260), (255, 180, 90))
    bubble = safe_load('bubble.png', (400, 220), (255, 255, 255))

    text_tile = create_text()
    XCENTER = MAXX // 2 - text_tile.size[0] // 2

    # Stagger plan:
    #   panda + pingu slide in for first 80 frames
    #   bubble fades in starting at frame 80, holds for 20
    #   text rises from below starting at frame 100
    panda_xs = sine_move(-panda.size[0] - 20, MAXX // 4 - 130, 80) \
               + [MAXX // 4 - 130] * (N_FRAMES - 80)
    pingu_xs = sine_move(MAXX + 20, 3 * MAXX // 4 - 130, 80) \
               + [3 * MAXX // 4 - 130] * (N_FRAMES - 80)
    bubble_alpha = [0] * 80 + sine_move(0, 255, 30) + [255] * (N_FRAMES - 110)
    text_ys = [200] * 100 + sine_move(200, 30, 40) + [30] * (N_FRAMES - 140)

    # Pad to exact length
    def pad(seq, n=N_FRAMES, fill=None):
        if len(seq) >= n:
            return seq[:n]
        return seq + [seq[-1] if fill is None else fill] * (n - len(seq))

    panda_xs = pad(panda_xs)
    pingu_xs = pad(pingu_xs)
    bubble_alpha = pad(bubble_alpha)
    text_ys = pad(text_ys)

    frames = []
    for f in range(N_FRAMES):
        bg = Image.new('RGB', (MAXX, MAXY), (255, 255, 255))

        bg.paste(panda, (panda_xs[f], YCHARS), panda)
        bg.paste(pingu, (pingu_xs[f], YCHARS), pingu)

        # Bubble with fade
        if bubble_alpha[f] > 0:
            faded = bubble.copy()
            alpha = faded.split()[-1]
            faded.putalpha(alpha.point(
                lambda a: int(a * bubble_alpha[f] / 255)
            ))
            bg.paste(
                faded,
                (XCENTER - 20, YCHARS - 100),
                faded,
            )

        # Text rising
        if text_ys[f] < 200:
            bg.paste(text_tile, (XCENTER, YCHARS - 80 + text_ys[f]))

        # Crop to the central viewport for aesthetic margins
        cropped = bg.crop((MAXX // 6, 100, 5 * MAXX // 6, 100 + MAXY - 200))
        frames.append(cropped)

    frames[0].save(
        'thank_you_animation.gif',
        save_all=True,
        append_images=frames[1:],
        duration=60,
        loop=0,
        optimize=True,
    )
    frames[N_FRAMES // 2].save('thank_you_still.png')
    print(f"Saved thank_you_animation.gif — {N_FRAMES} frames")


if __name__ == '__main__':
    main()
