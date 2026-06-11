"""
umap_demo.py - UMAP-style manifold visualisation on the sklearn digits.

This project doesn't ship umap-learn as a dependency, so we use the
closely-related Isomap (geodesic-distance MDS) plus t-SNE as
comparison baselines. The conceptual lesson — manifolds are preserved
when you respect the local neighbourhood graph — is the same.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits, make_swiss_roll
from sklearn.manifold import TSNE, Isomap
from sklearn.decomposition import PCA

RANDOM_STATE = 0
BG = '#0a0c18'
PALETTE = [
    '#ff7a90', '#80c6ff', '#ffd366', '#a4f0a4', '#cba0ff',
    '#ffb060', '#7fe0c0', '#ff9ec0', '#9fb3ff', '#e0e2a0',
]


def render_swiss_roll():
    X, t = make_swiss_roll(n_samples=1500, noise=0.05,
                           random_state=RANDOM_STATE)
    pca = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(X)
    iso = Isomap(n_neighbors=10, n_components=2).fit_transform(X)

    fig = plt.figure(figsize=(13, 4.5), facecolor=BG, dpi=110)
    ax0 = fig.add_subplot(1, 3, 1, projection='3d')
    ax0.set_facecolor(BG)
    ax0.scatter(X[:, 0], X[:, 1], X[:, 2], c=t, cmap='viridis', s=8)
    ax0.set_title('3D Swiss roll', color='#dde2ee', fontsize=10)
    ax0.set_xticks([]); ax0.set_yticks([]); ax0.set_zticks([])
    ax0.xaxis.set_pane_color((0, 0, 0, 0))
    ax0.yaxis.set_pane_color((0, 0, 0, 0))
    ax0.zaxis.set_pane_color((0, 0, 0, 0))

    for i, (emb, name) in enumerate([(pca, 'PCA'), (iso, 'Isomap (UMAP-like)')]):
        ax = fig.add_subplot(1, 3, i + 2)
        ax.set_facecolor(BG)
        ax.scatter(emb[:, 0], emb[:, 1], c=t, cmap='viridis', s=10)
        ax.set_title(name, color='#dde2ee', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('umap_swiss_roll.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_digits_comparison():
    digits = load_digits()
    X, y = digits.data, digits.target

    iso = Isomap(n_neighbors=15, n_components=2).fit_transform(X)
    tsne = TSNE(n_components=2, perplexity=30, max_iter=600,
                random_state=RANDOM_STATE).fit_transform(X)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5),
                             facecolor=BG, dpi=110)
    for ax, emb, name in [
        (axes[0], iso, 'Isomap (UMAP-like)'),
        (axes[1], tsne, 't-SNE'),
    ]:
        ax.set_facecolor(BG)
        for cls in range(10):
            mask = y == cls
            ax.scatter(emb[mask, 0], emb[mask, 1], s=14,
                       c=PALETTE[cls], edgecolors='none', alpha=0.85,
                       label=str(cls))
        ax.set_title(name, color='#dde2ee', fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('umap_vs_tsne.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    render_swiss_roll()
    render_digits_comparison()
    print('Wrote umap_swiss_roll.png, umap_vs_tsne.png')


if __name__ == '__main__':
    main()
