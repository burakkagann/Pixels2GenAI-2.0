"""
projection_map.py — warp a source image onto an off-angle target surface
using a homography (perspective transform). Same algorithm a projectionist
uses to align a projector beam with a building facade. Renders both the
source image and the warped result side-by-side.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (640, 480)
N_FRAMES = 60
FPS = 24


def make_source_image(size=(320, 200)):
    """Synthesise a colourful source content image (logo + gradient)."""
    w, h = size
    img = Image.new('RGB', size, (50, 30, 90))
    draw = ImageDraw.Draw(img)
    # Diagonal stripes
    for i in range(0, w + h, 28):
        draw.line([(i, 0), (i - h, h)], fill=(255, 180, 90), width=8)
    # Circle
    draw.ellipse([w // 2 - 40, h // 2 - 40, w // 2 + 40, h // 2 + 40],
                 fill=(255, 240, 220), outline=(30, 30, 60), width=3)
    # Text
    draw.text((w // 2 - 38, h // 2 - 8), 'PROJ',
              fill=(30, 30, 60))
    return img


def homography_from_corners(src_corners, dst_corners):
    """Solve for the 3x3 homography matrix that maps src_corners to dst_corners."""
    A = []
    b = []
    for (sx, sy), (dx, dy) in zip(src_corners, dst_corners):
        A.append([sx, sy, 1, 0, 0, 0, -dx * sx, -dx * sy])
        b.append(dx)
        A.append([0, 0, 0, sx, sy, 1, -dy * sx, -dy * sy])
        b.append(dy)
    A = np.array(A, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    h, *_ = np.linalg.lstsq(A, b, rcond=None)
    H = np.array([
        [h[0], h[1], h[2]],
        [h[3], h[4], h[5]],
        [h[6], h[7], 1.0],
    ])
    return H


def warp_image(src_arr, H_inv, dst_size, dst_corners):
    """Warp src into dst space by inverse sampling.

    For each pixel (xd, yd) in dst, compute (xs, ys) via H_inv and sample src."""
    dst_w, dst_h = dst_size
    sh, sw, _ = src_arr.shape

    # Bounding box of target quad
    xs = [p[0] for p in dst_corners]
    ys = [p[1] for p in dst_corners]
    x0, x1 = max(0, int(min(xs))), min(dst_w, int(max(xs)))
    y0, y1 = max(0, int(min(ys))), min(dst_h, int(max(ys)))

    out = np.zeros((dst_h, dst_w, 3), dtype=np.uint8)

    yy, xx = np.mgrid[y0:y1, x0:x1]
    # Homogeneous destination coords
    hom = np.stack([xx, yy, np.ones_like(xx)], axis=-1)
    src_hom = hom @ H_inv.T
    src_x = src_hom[..., 0] / src_hom[..., 2]
    src_y = src_hom[..., 1] / src_hom[..., 2]

    inside = (src_x >= 0) & (src_x < sw - 1) & (src_y >= 0) & (src_y < sh - 1)
    src_xi = np.clip(src_x.astype(int), 0, sw - 1)
    src_yi = np.clip(src_y.astype(int), 0, sh - 1)

    # Write samples into output bounded by the target quad
    sampled = src_arr[src_yi, src_xi]
    out[y0:y1, x0:x1][inside] = sampled[inside]
    return out


# Source content
source_w, source_h = 320, 200
source_img = make_source_image((source_w, source_h))
source_arr = np.array(source_img)

# Source corners — the rectangle itself
src_corners = [(0, 0), (source_w, 0), (source_w, source_h), (0, source_h)]

frames = []
for f in range(N_FRAMES):
    t = f / (N_FRAMES - 1)

    # Animate the destination quad as if the projector were tilting
    swing = math.sin(2 * math.pi * t) * 0.35
    cx_target = 320 + swing * 90
    # Define a trapezoid that simulates an off-axis projection
    dst_corners = [
        (cx_target - 140, 100),                # top-left
        (cx_target + 140 + int(swing * 100), 130),  # top-right (further away)
        (cx_target + 160, 360),                # bottom-right
        (cx_target - 160 + int(swing * 60), 380),   # bottom-left
    ]

    H = homography_from_corners(src_corners, dst_corners)
    H_inv = np.linalg.inv(H)

    warped = warp_image(source_arr, H_inv, SIZE, dst_corners)

    # Compose final frame
    canvas = Image.new('RGB', SIZE, (16, 20, 30))
    canvas_arr = np.array(canvas)
    canvas_arr = np.maximum(canvas_arr, warped)
    canvas = Image.fromarray(canvas_arr)
    draw = ImageDraw.Draw(canvas)

    # Draw target quad outline
    quad = dst_corners + [dst_corners[0]]
    draw.line(quad, fill=(255, 255, 110), width=2)

    # Caption
    draw.text((20, 18), 'Projection mapping — homography warp',
              fill=(220, 220, 240))
    draw.text((20, SIZE[1] - 36),
              'Source rectangle → warped onto target quad',
              fill=(160, 170, 200))

    frames.append(canvas)

frames[0].save(
    'projection_mapping.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 3].save('projection_mapping.png')

# Save the source image standalone for reference
source_img.save('source_content.png')
print(f"Saved projection_mapping.gif and projection_mapping.png — {N_FRAMES} frames")
