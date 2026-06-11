"""
tsne_demo.py - t-SNE on the sklearn digits dataset.

Show 1797 hand-drawn 8x8 digit images embedded in 2D where digits of the
same class cluster together. PCA on the same data is included as a
comparison panel — to make the non-linearity advantage visible.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# ---------- CONFIG ----------
RANDOM_STATE = 0
PERPLEXITY = 30
TSNE_ITER = 1000
BG = '#0a0c18'
PALETTE = [
    '#ff7a90', '#80c6ff', '#ffd366', '#a4f0a4', '#cba0ff',
    '#ffb060', '#7fe0c0', '#ff9ec0', '#9fb3ff', '#e0e2a0',
]
# ----------------------------


def render_pca_vs_tsne():
    digits = load_digits()
    X = digits.data
    y = digits.target

    pca = PCA(n_components=2, random_state=RANDOM_STATE).fit_transform(X)
    tsne = TSNE(n_components=2, perplexity=PERPLEXITY,
                max_iter=TSNE_ITER, random_state=RANDOM_STATE).fit_transform(X)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5),
                             facecolor=BG, dpi=110)
    for ax, embedding, title in [
        (axes[0], pca, 'PCA'),
        (axes[1], tsne, f't-SNE · perplexity={PERPLEXITY}'),
    ]:
        ax.set_facecolor(BG)
        for cls in range(10):
            mask = y == cls
            ax.scatter(embedding[mask, 0], embedding[mask, 1],
                       s=14, c=PALETTE[cls], edgecolors='none',
                       label=str(cls), alpha=0.85)
        ax.set_title(title, color='#dde2ee', fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=10,
               facecolor=BG, edgecolor='#3a4258', labelcolor='#dde2ee',
               fontsize=9, frameon=True)
    fig.tight_layout(rect=[0, 0.07, 1, 1])
    fig.savefig('tsne_vs_pca.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_perplexity_sweep():
    digits = load_digits()
    X = digits.data[:600]
    y = digits.target[:600]
    perplexities = [5, 15, 30, 60]
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.5),
                             facecolor=BG, dpi=110)
    for ax, p in zip(axes, perplexities):
        emb = TSNE(n_components=2, perplexity=p, max_iter=600,
                   random_state=RANDOM_STATE).fit_transform(X)
        ax.set_facecolor(BG)
        for cls in range(10):
            mask = y == cls
            ax.scatter(emb[mask, 0], emb[mask, 1], s=10,
                       c=PALETTE[cls], edgecolors='none', alpha=0.85)
        ax.set_title(f'perplexity = {p}', color='#dde2ee', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('tsne_perplexity_sweep.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    render_pca_vs_tsne()
    render_perplexity_sweep()
    print('Wrote tsne_vs_pca.png, tsne_perplexity_sweep.png')


if __name__ == '__main__':
    main()
