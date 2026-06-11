"""
kmeans_palette.py - K-Means colour quantisation. Treat every pixel of an
image as a point in RGB-space, cluster them into K groups, and replace
each pixel with the centroid of its cluster. The result is a posterised
version of the input that uses exactly K colours.

We also render the K-cluster centroids as a colour palette swatch beside
the original and the quantised output, so the algorithm's "vocabulary"
is visible.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
from sklearn.cluster import KMeans

# ---------- CONFIG ----------
WIDTH, HEIGHT = 384, 256
N_CLUSTERS = 6                  # K
N_SAMPLES = 4000                # subsample for fit speed
RANDOM_STATE = 0
# ----------------------------


def synthesise_input(width, height, seed=0):
    """Generate a synthetic input image with smooth gradients so the
    quantisation effect is easy to see without depending on an external file."""
    rng = np.random.default_rng(seed)
    ys, xs = np.meshgrid(np.linspace(0, 1, height), np.linspace(0, 1, width), indexing='ij')
    r = 0.5 + 0.5 * np.cos(2 * np.pi * (xs * 1.3 + ys * 0.9))
    g = 0.5 + 0.5 * np.sin(2 * np.pi * (xs * 0.7 - ys * 1.1))
    b = 0.5 + 0.5 * np.cos(2 * np.pi * (xs * 0.4 + ys * 2.2 + 0.3))
    base = np.stack([r, g, b], axis=-1)
    noise = rng.normal(0, 0.04, base.shape)
    img = np.clip(base + noise, 0, 1) * 255
    return img.astype(np.uint8)


def kmeans_quantise(image_rgb, k, n_samples=4000, random_state=0):
    """Return (quantised_image, sorted_palette_rgb_uint8)."""
    h, w, _ = image_rgb.shape
    pixels = image_rgb.reshape(-1, 3).astype(np.float32)

    rng = np.random.default_rng(random_state)
    idx = rng.choice(pixels.shape[0], size=min(n_samples, pixels.shape[0]),
                     replace=False)
    train = pixels[idx]

    km = KMeans(n_clusters=k, n_init=10, random_state=random_state)
    km.fit(train)

    labels = km.predict(pixels)
    quantised = km.cluster_centers_[labels].reshape(h, w, 3)
    quantised = np.clip(quantised, 0, 255).astype(np.uint8)

    # Sort palette by luminance for stable visual order.
    centres = km.cluster_centers_.clip(0, 255).astype(np.uint8)
    luma = centres @ np.array([0.299, 0.587, 0.114])
    order = np.argsort(luma)
    palette = centres[order]
    return quantised, palette


def palette_strip(palette, swatch=72, height=120):
    """Render the K colours as a horizontal swatch strip."""
    k = len(palette)
    img = Image.new('RGB', (k * swatch, height), (12, 14, 22))
    draw = ImageDraw.Draw(img)
    for i, c in enumerate(palette):
        draw.rectangle([i * swatch + 4, 10, (i + 1) * swatch - 4, height - 10],
                       fill=tuple(int(v) for v in c))
    return np.array(img)


def stack_panel(input_img, quantised_img, palette_strip_img):
    """Compose a three-panel figure: input | quantised | palette."""
    h = input_img.shape[0]
    spacer = np.full((h, 16, 3), 14, dtype=np.uint8)
    top = np.hstack([input_img, spacer, quantised_img])
    pad = np.full((20, top.shape[1], 3), 14, dtype=np.uint8)
    p_h, p_w, _ = palette_strip_img.shape
    palette_padded = np.full((p_h, top.shape[1], 3), 14, dtype=np.uint8)
    x0 = (top.shape[1] - p_w) // 2
    palette_padded[:, x0:x0 + p_w] = palette_strip_img
    return np.vstack([top, pad, palette_padded])


def main():
    image = synthesise_input(WIDTH, HEIGHT, seed=4)
    quantised, palette = kmeans_quantise(image, N_CLUSTERS,
                                         n_samples=N_SAMPLES,
                                         random_state=RANDOM_STATE)

    Image.fromarray(image).save('kmeans_input.png')
    Image.fromarray(quantised).save('kmeans_output.png')

    strip = palette_strip(palette, swatch=72, height=110)
    Image.fromarray(strip).save('kmeans_palette.png')

    panel = stack_panel(image, quantised, strip)
    Image.fromarray(panel).save('kmeans_panel.png')
    print(f'Wrote kmeans_input.png, kmeans_output.png, kmeans_palette.png, '
          f'kmeans_panel.png (K={N_CLUSTERS})')


if __name__ == '__main__':
    main()
