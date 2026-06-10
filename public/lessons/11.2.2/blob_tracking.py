"""
blob_tracking.py — given a binary motion mask from 11.2.1, identify
connected components (blobs), assign each a persistent ID, and track
them across frames by nearest-centroid association. Demonstrates the
mask -> contours -> centroids -> tracks pipeline.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (560, 360)
N_FRAMES = 90
COLORS = [(255, 110, 90), (110, 200, 255), (220, 200, 80),
          (180, 130, 240), (110, 240, 160), (255, 160, 200)]


def synth_frame(idx, n=N_FRAMES, size=SIZE):
    """Three blobs moving along different paths."""
    w, h = size
    arr = np.full((h, w, 3), [22, 24, 36], dtype=np.uint8)
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    t = idx / (n - 1)

    centres = []
    # Blob 1: horizontal sweep, left to right
    cx1 = int(40 + (w - 80) * t)
    cy1 = h // 2 + int(20 * math.sin(2 * math.pi * t))
    draw.ellipse([cx1 - 18, cy1 - 18, cx1 + 18, cy1 + 18], fill=(220, 110, 90))
    centres.append((cx1, cy1))

    # Blob 2: circular orbit around the centre
    angle = 2 * math.pi * t * 1.4
    cx2 = w // 2 + int(90 * math.cos(angle))
    cy2 = h // 2 + int(70 * math.sin(angle))
    draw.ellipse([cx2 - 20, cy2 - 20, cx2 + 20, cy2 + 20], fill=(120, 200, 255))
    centres.append((cx2, cy2))

    # Blob 3: diagonal sweep, bottom-left to top-right
    cx3 = int(40 + (w - 80) * t)
    cy3 = int((h - 40) - (h - 80) * t)
    draw.ellipse([cx3 - 22, cy3 - 22, cx3 + 22, cy3 + 22], fill=(220, 200, 80))
    centres.append((cx3, cy3))

    return np.array(img), centres


def find_blobs(arr, intensity_threshold=80):
    """Return list of (centroid_x, centroid_y, area) for bright regions.

    Uses a simple flood-fill on a boolean mask (the test image has
    only the three blobs above the threshold)."""
    gray = (arr[..., 0].astype(np.float32) + arr[..., 1].astype(np.float32)
            + arr[..., 2].astype(np.float32)) / 3
    mask = gray > intensity_threshold

    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    blobs = []

    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            # BFS
            stack = [(y, x)]
            visited[y, x] = True
            xs, ys = [], []
            while stack:
                cy, cx = stack.pop()
                xs.append(cx)
                ys.append(cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = cy + dy, cx + dx
                        if (0 <= ny < h and 0 <= nx < w and
                                mask[ny, nx] and not visited[ny, nx]):
                            visited[ny, nx] = True
                            stack.append((ny, nx))
            if len(xs) > 25:
                blobs.append((sum(xs) / len(xs), sum(ys) / len(ys), len(xs)))

    return blobs


def associate(prev_tracks, new_centres, max_dist=80):
    """Greedy nearest-centroid association. Returns new tracks dict."""
    new_tracks = {}
    used = set()

    for tid, (px, py, _) in prev_tracks.items():
        best_idx, best_dist = None, max_dist
        for i, (nx, ny, _) in enumerate(new_centres):
            if i in used:
                continue
            d = math.hypot(nx - px, ny - py)
            if d < best_dist:
                best_dist = d
                best_idx = i
        if best_idx is not None:
            new_tracks[tid] = new_centres[best_idx]
            used.add(best_idx)

    # Assign new IDs to unmatched centres
    next_id = max(prev_tracks.keys(), default=-1) + 1
    for i, c in enumerate(new_centres):
        if i not in used:
            new_tracks[next_id] = c
            next_id += 1

    return new_tracks


def render_tracks(arr, tracks, trails):
    img = Image.fromarray(arr)
    draw = ImageDraw.Draw(img)
    for tid, (x, y, area) in tracks.items():
        color = COLORS[tid % len(COLORS)]
        # Bounding circle
        r = int(math.sqrt(area / math.pi)) + 4
        draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=2)
        # ID label
        draw.text((x - 12, y - r - 18), f'ID {tid}', fill=color)
        # Trail
        if tid in trails:
            for px, py in trails[tid][-30:]:
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=color)
    return img


tracks = {}
trails = {}
frames = []
for f in range(N_FRAMES):
    arr, _ = synth_frame(f)
    centres = find_blobs(arr)
    tracks = associate(tracks, centres)
    # Append to trail history
    for tid, (x, y, _) in tracks.items():
        trails.setdefault(tid, []).append((x, y))
    frames.append(render_tracks(arr, tracks, trails))

frames[0].save(
    'blob_tracking.gif',
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True,
)
frames[N_FRAMES * 2 // 3].save('blob_tracking.png')
print(f"Saved blob_tracking.gif and blob_tracking.png — {N_FRAMES} frames")
