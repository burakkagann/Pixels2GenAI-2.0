"""
decision_tree_starter.py - Implement a single tree split from scratch.

Setup and visualisation are wired up. You implement `best_split()` -
find the (feature, threshold) pair that maximises information gain
(equivalently: minimises weighted Gini impurity).

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification


def gini(y):
    """Gini impurity of a label array. Lower = purer."""
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    p = counts / counts.sum()
    return 1.0 - (p * p).sum()


def best_split(X, y):
    """TODO: scan every (feature, threshold) and return the one with
    the lowest weighted Gini impurity after the split.

    For each column j:
      for each unique value v in X[:, j]:
        mask = X[:, j] <= v
        left, right = y[mask], y[~mask]
        if len(left) == 0 or len(right) == 0:
            continue
        score = (len(left) * gini(left) + len(right) * gini(right)) / len(y)
        track the minimum score.

    Return (best_feature_idx, best_threshold).
    """
    return 0, 0.0


def render(X, y, feat, thr):
    fig, ax = plt.subplots(figsize=(6, 5.5), facecolor='#0a0c18', dpi=110)
    ax.set_facecolor('#0a0c18')
    palette = ['#ff7a90', '#80c6ff', '#ffd366']
    for cls in sorted(set(y)):
        mask = y == cls
        ax.scatter(X[mask, 0], X[mask, 1], s=24,
                   c=palette[cls], edgecolors='white', linewidths=0.5)
    if feat == 0:
        ax.axvline(thr, color='white', linewidth=1.4, alpha=0.85)
    else:
        ax.axhline(thr, color='white', linewidth=1.4, alpha=0.85)
    ax.set_title(f'best split: x[{feat}] = {thr:.2f}',
                 color='#dde2ee', fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig('decision_tree_starter.png', facecolor='#0a0c18', dpi=110)


def main():
    X, y = make_classification(n_samples=300, n_features=2,
                               n_informative=2, n_redundant=0,
                               n_classes=3, n_clusters_per_class=1,
                               class_sep=1.4, random_state=0)
    feat, thr = best_split(X, y)
    print(f'best split: feature {feat} at threshold {thr:.3f}')
    render(X, y, feat, thr)


if __name__ == '__main__':
    main()
