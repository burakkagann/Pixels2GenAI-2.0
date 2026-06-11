"""
dbscan_patterns.py - DBSCAN clustering on a 2D point cloud. Demonstrates
the algorithm's signature property: it finds arbitrarily-shaped clusters
(crescents, rings) that K-Means cannot, and explicitly labels outliers
as "noise" rather than forcing them into a cluster.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, KMeans
from sklearn.datasets import make_moons, make_blobs

# ---------- CONFIG ----------
N_POINTS = 600
NOISE = 0.08
DBSCAN_EPS = 0.20
DBSCAN_MIN_SAMPLES = 7
KMEANS_K = 2
RANDOM_STATE = 0

PALETTE = ['#ff7a90', '#80c6ff', '#ffd366', '#a4f0a4', '#cba0ff']
NOISE_COLOUR = '#5a6072'
BG = '#0a0c18'
# ----------------------------


def render_dbscan_vs_kmeans():
    rng = np.random.default_rng(RANDOM_STATE)
    X_moons, _ = make_moons(n_samples=N_POINTS, noise=NOISE,
                            random_state=RANDOM_STATE)

    # Add some scattered outliers
    outliers = rng.uniform(-1.5, 2.5, size=(40, 2))
    X = np.vstack([X_moons, outliers])

    db = DBSCAN(eps=DBSCAN_EPS, min_samples=DBSCAN_MIN_SAMPLES).fit(X)
    km = KMeans(n_clusters=KMEANS_K, n_init=10,
                random_state=RANDOM_STATE).fit(X)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6),
                             facecolor=BG, dpi=110)

    for ax, labels, title in [
        (axes[0], km.labels_, f'K-Means (K={KMEANS_K})'),
        (axes[1], db.labels_, f'DBSCAN (eps={DBSCAN_EPS}, min_samples={DBSCAN_MIN_SAMPLES})'),
    ]:
        ax.set_facecolor(BG)
        unique = sorted(set(labels))
        for lab in unique:
            mask = labels == lab
            colour = NOISE_COLOUR if lab == -1 else PALETTE[lab % len(PALETTE)]
            size = 14 if lab == -1 else 22
            edge = (1, 1, 1, 0.0)
            ax.scatter(X[mask, 0], X[mask, 1], s=size, c=colour,
                       edgecolors=edge, linewidths=0.4)
        ax.set_title(title, color='#dde2ee', fontsize=11)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('dbscan_comparison.png', facecolor=BG, dpi=110)
    plt.close(fig)

    # Plot just DBSCAN with a "core / border / noise" colouring
    fig, ax = plt.subplots(figsize=(6, 5.5), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    core_mask = np.zeros_like(db.labels_, dtype=bool)
    core_mask[db.core_sample_indices_] = True
    unique = sorted(set(db.labels_))
    for lab in unique:
        if lab == -1:
            mask = db.labels_ == -1
            ax.scatter(X[mask, 0], X[mask, 1], s=14, c=NOISE_COLOUR,
                       label='noise')
            continue
        cluster_mask = db.labels_ == lab
        ax.scatter(X[cluster_mask & core_mask, 0], X[cluster_mask & core_mask, 1],
                   s=42, c=PALETTE[lab % len(PALETTE)],
                   edgecolors='white', linewidths=0.6,
                   label=f'cluster {lab} core')
        ax.scatter(X[cluster_mask & ~core_mask, 0], X[cluster_mask & ~core_mask, 1],
                   s=18, c=PALETTE[lab % len(PALETTE)], alpha=0.65,
                   label=f'cluster {lab} border')
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title('DBSCAN: core, border, noise', color='#dde2ee', fontsize=11)
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    ax.legend(loc='lower left', fontsize=8, facecolor='#181b27',
              edgecolor='#3a4258', labelcolor='#dde2ee')
    fig.tight_layout()
    fig.savefig('dbscan_core_border_noise.png', facecolor=BG, dpi=110)
    plt.close(fig)

    n_clusters = len(set(db.labels_) - {-1})
    n_noise = int(np.sum(db.labels_ == -1))
    print(f'DBSCAN: {n_clusters} clusters, {n_noise} noise points')
    print(f'K-Means: {KMEANS_K} clusters (no noise concept)')


if __name__ == '__main__':
    render_dbscan_vs_kmeans()
