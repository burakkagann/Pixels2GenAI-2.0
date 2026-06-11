"""
meanshift_segment.py - Mean-Shift segmentation. Treat each pixel as a
point in a 5D feature space (R, G, B, x, y) and iteratively shift it
toward the local mean of nearby points until it converges. Pixels that
converge to the same point belong to the same segment.

We don't actually do per-pixel shifting (that is O(n^2) and ~slow on
images); we use sklearn's MeanShift on a sub-sample of pixels and then
do a nearest-centroid lookup for the full image.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
from sklearn.cluster import MeanShift, estimate_bandwidth

# ---------- CONFIG ----------
WIDTH, HEIGHT = 360, 240
SAMPLE_PIXELS = 2500
SPATIAL_WEIGHT = 0.4        # 0 = colour only; 1 = colour and spatial equal
RANDOM_STATE = 0
# ----------------------------


def synthesise_input(width, height, seed=2):
    """Three coloured blobs on a blue background — simple but enough
    for Mean-Shift to find natural cluster modes."""
    rng = np.random.default_rng(seed)
    img = np.zeros((height, width, 3), dtype=np.float32)
    img[:] = (30, 50, 120)
    centres = [
        (width * 0.25, height * 0.35, 100, 30, 50,  (235, 110, 90)),
        (width * 0.70, height * 0.30, 120, 40, 60,  (245, 200, 70)),
        (width * 0.50, height * 0.75, 140, 30, 40,  (90, 200, 140)),
    ]
    ys, xs = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    for cx, cy, rx, ry, soft, colour in centres:
        falloff = np.exp(
            -(((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2)
        )
        for ch in range(3):
            img[..., ch] = img[..., ch] * (1 - falloff) + colour[ch] * falloff
    noise = rng.normal(0, 6.0, img.shape)
    return np.clip(img + noise, 0, 255).astype(np.uint8)


def build_features(image, spatial_weight):
    """5D feature vector per pixel: (R, G, B, alpha*x, alpha*y)."""
    h, w, _ = image.shape
    ys, xs = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
    flat_rgb = image.reshape(-1, 3).astype(np.float32)
    flat_x = (xs / w * 255 * spatial_weight).reshape(-1, 1)
    flat_y = (ys / h * 255 * spatial_weight).reshape(-1, 1)
    return np.hstack([flat_rgb, flat_x, flat_y])


def main():
    rng = np.random.default_rng(RANDOM_STATE)
    image = synthesise_input(WIDTH, HEIGHT)
    Image.fromarray(image).save('meanshift_input.png')

    features = build_features(image, SPATIAL_WEIGHT)
    idx = rng.choice(features.shape[0], size=SAMPLE_PIXELS, replace=False)
    train = features[idx]

    bandwidth = 50.0       # tuned by hand for the synthetic input
    print(f'using bandwidth = {bandwidth:.2f}')

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(train)
    centres = ms.cluster_centers_       # (k, 5)
    n_clusters = len(centres)
    print(f'found {n_clusters} modes')

    # Nearest-centroid lookup for every pixel
    # (the 5D centroid uses RGB+xy; we replace with the RGB part only)
    diff = features[:, None, :] - centres[None, :, :]
    dist = np.linalg.norm(diff, axis=-1)
    labels = dist.argmin(axis=1)
    output = centres[labels, :3].clip(0, 255).astype(np.uint8)
    output = output.reshape(HEIGHT, WIDTH, 3)
    Image.fromarray(output).save('meanshift_segments.png')

    # Side-by-side panel
    spacer = np.full((HEIGHT, 12, 3), 14, dtype=np.uint8)
    panel = np.hstack([image, spacer, output])
    Image.fromarray(panel).save('meanshift_panel.png')

    print(f'Wrote meanshift_input.png, meanshift_segments.png, meanshift_panel.png '
          f'({n_clusters} modes)')


if __name__ == '__main__':
    main()
