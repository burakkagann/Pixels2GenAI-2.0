"""
ARCHIVED one-shot from the flat-layout era: writes into public/lessons/<id>/,
which the 2026-06 restructure replaced with public/lesson-media/<module>/<subtopic>/<leaf>/.
Outputs are already committed; rework the paths before ever running again.

Generate figures for Module 09 — Neural Networks.

The 9.3 (Training Dynamics) and 9.4 (Feature Visualization) lessons
were stub READMEs in v1. This script materialises the demo PNGs each
from-scratch MDX references using pure-NumPy implementations of the
underlying ideas (loss landscapes, gradient descent paths, dream-like
filter activations, attention heatmaps).

Run from project root:
    python scripts/gen-module-09-figures.py
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "public" / "lessons"
SEED = 9


def normalise(z):
    return (z - z.min()) / (z.max() - z.min() + 1e-12)


def save_gray(arr01, path):
    out = (np.clip(arr01, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out, "L").save(path)


def save_rgb(arr01, path):
    out = (np.clip(arr01, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out).save(path)


# --------------------------------------------------------------------
# 9.3.1 Loss landscape: contour map of (w1, w2) → loss
# --------------------------------------------------------------------
def gen_9_3_1():
    d = LESSONS_DIR / "9.3.1"; d.mkdir(parents=True, exist_ok=True)

    # Build a synthetic loss landscape with multiple minima
    w1, w2 = np.linspace(-3, 3, 400), np.linspace(-3, 3, 400)
    W1, W2 = np.meshgrid(w1, w2)
    loss = (W1**2 + W2**2) * 0.1 + 0.7 * np.exp(-((W1 - 1.5)**2 + (W2 - 1.0)**2)) \
         + 0.5 * np.exp(-((W1 + 1.2)**2 + (W2 + 1.4)**2)) \
         - 0.6 * np.exp(-((W1 - 0.3)**2 + (W2 - 0.4)**2) * 2.5)

    # Render as a viridis-like grayscale gradient
    z = normalise(loss)
    save_gray(z, d / "loss_landscape_2d.png")

    # Stepped contour view to highlight basins
    bands = (z * 12).astype(np.int32)
    contour = ((bands * 21) % 256).astype(np.uint8)
    Image.fromarray(contour, "L").save(d / "loss_landscape_contours.png")

    # Surface heat-map colour version
    rgb = np.zeros((*z.shape, 3))
    rgb[..., 0] = np.clip(z * 1.6 - 0.3, 0, 1)
    rgb[..., 1] = np.clip(1.2 - z * 1.5, 0, 1) * 0.6
    rgb[..., 2] = np.clip(0.7 - z * 0.5, 0, 1)
    save_rgb(rgb, d / "loss_landscape_color.png")

    print("9.3.1 done")


# --------------------------------------------------------------------
# 9.3.2 Gradient descent: draw the path on the loss landscape
# --------------------------------------------------------------------
def gen_9_3_2():
    d = LESSONS_DIR / "9.3.2"; d.mkdir(parents=True, exist_ok=True)

    # Quadratic-bowl loss with one minimum
    w1, w2 = np.linspace(-3, 3, 400), np.linspace(-3, 3, 400)
    W1, W2 = np.meshgrid(w1, w2)
    loss = 0.5 * (W1 - 0.5)**2 + 1.5 * (W2 + 0.3)**2

    # Background image (grayscale contour)
    z = normalise(loss)
    bg = (z * 200).astype(np.uint8)
    img = Image.fromarray(bg, "L").convert("RGB")
    draw = ImageDraw.Draw(img)

    def coord_to_px(c1, c2):
        # Map (w1, w2) in [-3, 3] to pixel coordinate
        px = (c1 + 3) / 6 * 399
        py = (c2 + 3) / 6 * 399
        return int(px), int(py)

    # Gradient descent path
    def grad(c1, c2):
        return np.array([(c1 - 0.5), 3.0 * (c2 + 0.3)])

    path = [(2.5, 2.5)]
    lr = 0.15
    for _ in range(40):
        c1, c2 = path[-1]
        g = grad(c1, c2)
        path.append((c1 - lr * g[0], c2 - lr * g[1]))

    # Draw path
    px_path = [coord_to_px(c1, c2) for c1, c2 in path]
    for i in range(len(px_path) - 1):
        draw.line([px_path[i], px_path[i + 1]], fill=(220, 60, 40), width=2)
    for p in px_path:
        draw.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=(240, 240, 40))

    img.save(d / "gradient_descent_path.png")

    # Different learning-rate comparison
    fig_width = 800
    panel = Image.new("RGB", (fig_width, 400), (200, 200, 200))
    p_draw = ImageDraw.Draw(panel)
    # Three loss curves (steps vs loss) for lr = small / good / too-big
    def trace(lr):
        c = np.array([2.5, 2.5])
        losses = []
        for _ in range(50):
            losses.append(0.5 * (c[0] - 0.5)**2 + 1.5 * (c[1] + 0.3)**2)
            c = c - lr * np.array([(c[0] - 0.5), 3.0 * (c[1] + 0.3)])
        return losses
    traces = [("lr=0.05 slow", trace(0.05), (60, 120, 200)),
              ("lr=0.15 good", trace(0.15), (60, 180, 60)),
              ("lr=0.55 diverge", trace(0.55), (220, 60, 40))]
    # Plot on the panel
    for label, ys, color in traces:
        ys = np.array(ys)
        ys = ys / ys[0]
        for i in range(len(ys) - 1):
            x0 = int(i / len(ys) * (fig_width - 40)) + 20
            x1 = int((i + 1) / len(ys) * (fig_width - 40)) + 20
            y0 = 380 - int(np.clip(ys[i] * 350, 0, 350))
            y1 = 380 - int(np.clip(ys[i + 1] * 350, 0, 350))
            p_draw.line([(x0, y0), (x1, y1)], fill=color, width=2)
    panel.save(d / "learning_rate_comparison.png")
    print("9.3.2 done")


# --------------------------------------------------------------------
# 9.3.3 Overfitting / underfitting: polynomial fits
# --------------------------------------------------------------------
def gen_9_3_3():
    d = LESSONS_DIR / "9.3.3"; d.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED + 30)
    x = np.linspace(0, 1, 12)
    y_true = np.sin(2 * np.pi * x)
    y = y_true + rng.normal(0, 0.18, size=x.shape)

    W = 800
    H = 300
    panel = Image.new("RGB", (W, H), (245, 245, 245))
    draw = ImageDraw.Draw(panel)

    cols = [(60, 120, 200), (60, 180, 60), (220, 60, 40)]
    titles = ["underfit (deg 1)", "good (deg 3)", "overfit (deg 12)"]
    deg_list = [1, 3, 12]

    cell_w = W // 3
    for i, (deg, title, col) in enumerate(zip(deg_list, titles, cols)):
        coef = np.polyfit(x, y, deg)
        xs = np.linspace(0, 1, 200)
        ys = np.polyval(coef, xs)

        # Plot the data and fit in the cell
        def to_px(px_x, px_y, base_x):
            X = int(px_x * (cell_w - 40) + 20 + base_x)
            Y = int(H - 30 - (px_y + 1.5) / 3 * (H - 50))
            return X, Y
        base = i * cell_w
        # True curve (dashed-ish via short segments)
        for k in range(len(xs) - 1):
            X0, Y0 = to_px(xs[k], np.sin(2*np.pi*xs[k]), base)
            X1, Y1 = to_px(xs[k+1], np.sin(2*np.pi*xs[k+1]), base)
            if k % 4 < 2:
                draw.line([(X0, Y0), (X1, Y1)], fill=(160, 160, 160), width=1)
        # Fit
        for k in range(len(xs) - 1):
            X0, Y0 = to_px(xs[k], ys[k], base)
            X1, Y1 = to_px(xs[k+1], ys[k+1], base)
            draw.line([(X0, Y0), (X1, Y1)], fill=col, width=2)
        # Data points
        for px_x, px_y in zip(x, y):
            X, Y = to_px(px_x, px_y, base)
            draw.ellipse([X-3, Y-3, X+3, Y+3], fill=(30, 30, 30))
        # Title
        draw.text((base + 30, 5), title, fill=(20, 20, 20))

    panel.save(d / "overfit_underfit.png")
    print("9.3.3 done")


# --------------------------------------------------------------------
# 9.4.1 DeepDream: iterative gradient ascent on noise field
# --------------------------------------------------------------------
def gen_9_4_1():
    d = LESSONS_DIR / "9.4.1"; d.mkdir(parents=True, exist_ok=True)

    H = W = 400
    rng = np.random.default_rng(SEED + 40)
    img = rng.normal(0.5, 0.05, (H, W))

    # Iteratively amplify low-frequency components (simulates DeepDream
    # "enhancing what the network sees")
    for _ in range(80):
        # blur to extract low frequency
        from numpy.fft import fft2, ifft2, fftshift, ifftshift
        F = fftshift(fft2(img))
        h, w = img.shape
        cy, cx = h // 2, w // 2
        Y, X = np.indices((h, w))
        r2 = (X - cx)**2 + (Y - cy)**2
        mask = np.exp(-r2 / (2 * 25**2))   # gaussian low-pass
        low = np.real(ifft2(ifftshift(F * mask)))
        # add amplified low-frequency back
        img = img + 0.05 * (low - img.mean())
        img = np.clip(img, 0, 1)

    save_gray(normalise(img), d / "dream_before_after.png")

    # Pseudo-coloured "dreamy" version
    base = normalise(img)
    rgb = np.zeros((H, W, 3))
    rgb[..., 0] = np.clip(np.sin(base * 6) * 0.5 + 0.5, 0, 1)
    rgb[..., 1] = np.clip(np.sin(base * 4 + 1.0) * 0.5 + 0.5, 0, 1)
    rgb[..., 2] = np.clip(np.sin(base * 5 + 2.0) * 0.5 + 0.5, 0, 1)
    save_rgb(rgb, d / "dream_color.png")
    print("9.4.1 done")


# --------------------------------------------------------------------
# 9.4.2 Feature map art: stack of filtered versions of an input
# --------------------------------------------------------------------
def gen_9_4_2():
    d = LESSONS_DIR / "9.4.2"; d.mkdir(parents=True, exist_ok=True)

    # Synthetic input: concentric stripes + radial noise
    H, W = 200, 200
    y, x = np.indices((H, W)).astype(float)
    r = np.sqrt((y - H/2)**2 + (x - W/2)**2)
    base = (np.sin(r / 6) + 1) / 2

    # Six kernels with different orientations / scales
    kernels = []
    for angle_deg in [0, 30, 60, 90, 120, 150]:
        a = np.deg2rad(angle_deg)
        size = 7
        u = np.linspace(-1, 1, size)
        gx, gy = np.meshgrid(u, u)
        rot = gx * np.cos(a) + gy * np.sin(a)
        k = np.cos(rot * 3) * np.exp(-(gx**2 + gy**2) / 0.4)
        kernels.append(k / np.abs(k).sum())

    # Apply each filter and tile in a 2x3 grid
    panels = []
    for k in kernels:
        out = np.zeros_like(base)
        pad = k.shape[0] // 2
        padded = np.pad(base, pad, mode="edge")
        for i in range(H):
            for j in range(W):
                out[i, j] = np.sum(padded[i:i+k.shape[0], j:j+k.shape[1]] * k)
        panels.append(normalise(out))

    GAP = 6
    gap_h = np.zeros((H, GAP))
    gap_v = np.zeros((GAP, 3 * W + 2 * GAP))
    row1 = np.hstack([panels[0], gap_h, panels[1], gap_h, panels[2]])
    row2 = np.hstack([panels[3], gap_h, panels[4], gap_h, panels[5]])
    grid = np.vstack([row1, gap_v, row2])
    save_gray(grid, d / "feature_maps_grid.png")
    print("9.4.2 done")


# --------------------------------------------------------------------
# 9.4.3 Attention heatmap over an input
# --------------------------------------------------------------------
def gen_9_4_3():
    d = LESSONS_DIR / "9.4.3"; d.mkdir(parents=True, exist_ok=True)

    # Synthetic input: bright disc + rectangle on noisy bg
    H = W = 300
    rng = np.random.default_rng(SEED + 60)
    img = rng.normal(0.3, 0.05, (H, W))
    y, x = np.indices((H, W))
    disc = (x - 90)**2 + (y - 200)**2 < 35**2
    img[disc] = 0.85
    rect = (x > 170) & (x < 250) & (y > 80) & (y < 130)
    img[rect] = 0.7
    img = np.clip(img, 0, 1)

    # "Attention" heatmap — Gaussian blobs over the salient regions
    Y, X = np.indices((H, W))
    a1 = np.exp(-((X - 90)**2 + (Y - 200)**2) / (2 * 40**2))
    a2 = np.exp(-((X - 210)**2 + (Y - 105)**2) / (2 * 25**2))
    attention = normalise(a1 + a2)

    # Overlay attention as warm red on top of grayscale base
    base = np.stack([img, img, img], axis=-1)
    heat = np.zeros_like(base)
    heat[..., 0] = attention
    heat[..., 1] = attention * 0.4
    out = base * (1 - attention[..., None] * 0.6) + heat * (attention[..., None] * 0.6)
    save_rgb(out, d / "attention_overlay.png")

    # Plain heatmap
    save_gray(attention, d / "attention_map.png")
    print("9.4.3 done")


# --------------------------------------------------------------------
if __name__ == "__main__":
    gen_9_3_1()
    gen_9_3_2()
    gen_9_3_3()
    gen_9_4_1()
    gen_9_4_2()
    gen_9_4_3()
    print("all module 09 figures generated")
