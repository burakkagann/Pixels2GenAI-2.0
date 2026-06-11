"""
synthetic_webcam.py — emulate a webcam stream with a synthetic moving
scene, then demonstrate the capture/process/display pipeline plus motion
detection by frame differencing. Pillow + NumPy only; runs without a
camera.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (640, 480)
N_FRAMES = 40


def synth_frame(idx, n=N_FRAMES, size=SIZE):
    """Render frame `idx` of a synthetic scene: textured wall + moving disc."""
    rng = np.random.default_rng(0)        # stable wall texture
    w, h = size
    arr = np.full((h, w, 3), [38, 44, 60], dtype=np.uint8)

    # Wall texture: subtle noise
    noise = rng.integers(-12, 12, (h, w, 3), dtype=np.int32)
    arr = np.clip(arr.astype(np.int32) + noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)

    # Static landmarks
    draw.rectangle([40, 320, 200, 460], fill=(110, 80, 60))   # table
    draw.rectangle([520, 50, 600, 460], fill=(60, 90, 130))   # bookshelf

    # Moving disc: sinusoidal x position, slowly drifting y
    t = idx / (n - 1)
    cx = int(120 + 400 * (0.5 - 0.5 * math.cos(2 * math.pi * t)))
    cy = int(220 + 60 * math.sin(2 * math.pi * t))
    r = 36
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(255, 120, 80), outline=(40, 20, 10))

    return np.array(img)


def absdiff(a, b):
    """Per-pixel absolute difference; matches cv2.absdiff."""
    return np.abs(a.astype(np.int32) - b.astype(np.int32)).astype(np.uint8)


def threshold_binary(arr, t=25):
    """Binary threshold."""
    return (arr > t).astype(np.uint8) * 255


def to_gray(arr):
    """ITU-R BT.601 luma — same as cv2.cvtColor(..., COLOR_BGR2GRAY)."""
    return (arr[..., 0] * 0.114 + arr[..., 1] * 0.587 + arr[..., 2] * 0.299).astype(np.uint8)


# Render a four-panel still showing the pipeline at one frame
mid = N_FRAMES // 2
prev_arr = synth_frame(mid - 1)
curr_arr = synth_frame(mid)

prev_gray = to_gray(prev_arr)
curr_gray = to_gray(curr_arr)
diff = absdiff(prev_gray, curr_gray)
motion = threshold_binary(diff, t=20)

# Overlay green on motion
overlay = curr_arr.copy()
overlay[motion > 0] = [40, 255, 80]
result = (0.65 * curr_arr + 0.35 * overlay).astype(np.uint8)

# Composite 2x2 grid
GAP = 6
w, h = SIZE
grid = np.full((h * 2 + GAP, w * 2 + GAP, 3), 18, dtype=np.uint8)
grid[:h, :w] = prev_arr
grid[:h, w + GAP:] = curr_arr
grid[h + GAP:, :w] = np.stack([motion] * 3, axis=-1)
grid[h + GAP:, w + GAP:] = result
Image.fromarray(grid).save('pipeline_demo.png')

# Animate the full sequence as a GIF
frames_gif = []
prev_gray_loop = None
for f in range(N_FRAMES):
    cur = synth_frame(f)
    cur_gray = to_gray(cur)
    if prev_gray_loop is None:
        out = cur
    else:
        d = absdiff(prev_gray_loop, cur_gray)
        m = threshold_binary(d, t=20)
        over = cur.copy()
        over[m > 0] = [40, 255, 80]
        out = (0.65 * cur + 0.35 * over).astype(np.uint8)
    frames_gif.append(Image.fromarray(out))
    prev_gray_loop = cur_gray

frames_gif[0].save(
    'webcam_pipeline.gif',
    save_all=True,
    append_images=frames_gif[1:],
    duration=80,
    loop=0,
    optimize=True,
)

print(f"Saved pipeline_demo.png and webcam_pipeline.gif "
      f"({N_FRAMES} frames at synthetic 12 fps)")
