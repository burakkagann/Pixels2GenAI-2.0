"""
pca_palette.py - PCA on an image's pixel cloud in RGB space. The first
principal component is the dominant axis of colour variation; projecting
along it gives a one-dimensional palette gradient. The first two PCs
give a 2D scatter that summarises the image's whole colour content.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.decomposition import PCA

# ---------- CONFIG ----------
WIDTH, HEIGHT = 360, 240
N_COMPONENTS = 3
N_SCATTER = 4000
RANDOM_STATE = 0
BG = '#0a0c18'
# ----------------------------


def synthesise_input(width, height, seed=0):
    """A two-tone gradient with a small accent colour."""
    rng = np.random.default_rng(seed)
    ys, xs = np.meshgrid(np.linspace(0, 1, height), np.linspace(0, 1, width), indexing='ij')
    base = np.stack([
        0.30 + 0.55 * xs,
        0.10 + 0.30 * ys + 0.30 * xs,
        0.70 - 0.45 * xs,
    ], axis=-1)
    # accent: a small dense patch of warm yellow
    mask = ((xs - 0.75) ** 2 + (ys - 0.30) ** 2) < 0.02
    base[mask] = (0.95, 0.80, 0.30)
    noise = rng.normal(0, 0.02, base.shape)
    return np.clip((base + noise) * 255, 0, 255).astype(np.uint8)


def render_pca_panel():
    image = synthesise_input(WIDTH, HEIGHT)
    pixels = image.reshape(-1, 3).astype(np.float32) / 255.0

    pca = PCA(n_components=N_COMPONENTS, random_state=RANDOM_STATE).fit(pixels)
    projected = pca.transform(pixels)
    explained = pca.explained_variance_ratio_

    # Render a 1D palette from PC1 (sample 12 equally-spaced points along it)
    pc1_min, pc1_max = projected[:, 0].min(), projected[:, 0].max()
    n_swatches = 12
    pc1_grid = np.linspace(pc1_min, pc1_max, n_swatches)
    # Combine with mean of PC2, PC3 to reconstruct full RGB
    extra = np.zeros((n_swatches, N_COMPONENTS - 1))
    palette = pca.inverse_transform(
        np.column_stack([pc1_grid.reshape(-1, 1), extra])
    )
    palette = np.clip(palette, 0, 1)

    # Subsample for the scatter plot
    rng = np.random.default_rng(RANDOM_STATE)
    idx = rng.choice(len(projected), size=N_SCATTER, replace=False)

    fig = plt.figure(figsize=(11, 7.5), facecolor=BG, dpi=110)
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1])

    ax_img = fig.add_subplot(gs[0, 0])
    ax_img.imshow(image)
    ax_img.set_title('Input image', color='#dde2ee', fontsize=10)
    ax_img.set_xticks([]); ax_img.set_yticks([])

    ax_sc = fig.add_subplot(gs[0, 1])
    ax_sc.set_facecolor(BG)
    colours = pixels[idx]
    ax_sc.scatter(projected[idx, 0], projected[idx, 1], s=4,
                  c=colours, alpha=0.8)
    ax_sc.set_xlabel(f'PC1 · {explained[0] * 100:.1f}% variance', color='#dde2ee')
    ax_sc.set_ylabel(f'PC2 · {explained[1] * 100:.1f}% variance', color='#dde2ee')
    ax_sc.set_title('Pixel cloud projected onto first two PCs',
                    color='#dde2ee', fontsize=10)
    ax_sc.tick_params(colors='#7f879a')
    for spine in ax_sc.spines.values():
        spine.set_color('#3a4258')

    ax_pal = fig.add_subplot(gs[1, :])
    ax_pal.set_facecolor(BG)
    for i, c in enumerate(palette):
        ax_pal.add_patch(plt.Rectangle((i, 0), 1, 1, color=tuple(c)))
    ax_pal.set_xlim(0, n_swatches); ax_pal.set_ylim(0, 1)
    ax_pal.set_xticks([]); ax_pal.set_yticks([])
    ax_pal.set_title('Palette generated along PC1 (dominant colour axis)',
                     color='#dde2ee', fontsize=10)
    for spine in ax_pal.spines.values():
        spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('pca_panel.png', facecolor=BG, dpi=110)
    plt.close(fig)
    print(f'Explained variance: '
          f'{[f"{v * 100:.1f}%" for v in explained]}')


if __name__ == '__main__':
    render_pca_panel()
