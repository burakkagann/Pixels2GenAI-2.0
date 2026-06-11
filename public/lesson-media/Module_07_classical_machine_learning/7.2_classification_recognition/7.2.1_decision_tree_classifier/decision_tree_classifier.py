"""
decision_tree_classifier.py - Fit a decision tree on a 2D toy dataset
and visualise its decision boundary. The geometric story of a decision
tree is "axis-aligned rectangles tiling the plane", and rendering the
boundary makes that immediately obvious.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.datasets import make_classification

# ---------- CONFIG ----------
N_SAMPLES = 400
N_CLASSES = 3
MAX_DEPTHS = [1, 3, None]      # depths to show side by side
RANDOM_STATE = 0
BG = '#0a0c18'
PALETTE = ['#ff7a90', '#80c6ff', '#ffd366']
# ----------------------------


def make_data(seed):
    X, y = make_classification(
        n_samples=N_SAMPLES, n_features=2,
        n_informative=2, n_redundant=0, n_repeated=0,
        n_classes=N_CLASSES, n_clusters_per_class=1,
        class_sep=1.4, random_state=seed,
    )
    return X, y


def render_boundaries(X, y):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4),
                             facecolor=BG, dpi=110)

    xmin, xmax = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    ymin, ymax = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 220),
                         np.linspace(ymin, ymax, 220))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    cmap = matplotlib.colors.ListedColormap(PALETTE[:N_CLASSES])
    for ax, depth in zip(axes, MAX_DEPTHS):
        clf = DecisionTreeClassifier(max_depth=depth,
                                     random_state=RANDOM_STATE).fit(X, y)
        zz = clf.predict(grid).reshape(xx.shape)
        ax.set_facecolor(BG)
        ax.contourf(xx, yy, zz, alpha=0.35, cmap=cmap, levels=N_CLASSES - 1)
        for cls in range(N_CLASSES):
            mask = y == cls
            ax.scatter(X[mask, 0], X[mask, 1], s=24,
                       c=PALETTE[cls], edgecolors='white', linewidths=0.5)
        depth_str = 'unlimited' if depth is None else str(depth)
        train_acc = clf.score(X, y)
        ax.set_title(f'max_depth = {depth_str} · train accuracy {train_acc:.2f}',
                     color='#dde2ee', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('decision_boundary.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_tree_diagram(X, y):
    clf = DecisionTreeClassifier(max_depth=3,
                                 random_state=RANDOM_STATE).fit(X, y)
    fig, ax = plt.subplots(figsize=(9, 6), facecolor=BG, dpi=110)
    plot_tree(clf, ax=ax, filled=True,
              feature_names=['x_0', 'x_1'],
              class_names=[f'C{c}' for c in range(N_CLASSES)],
              impurity=False, fontsize=8)
    fig.tight_layout()
    fig.savefig('tree_diagram.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    X, y = make_data(seed=RANDOM_STATE)
    render_boundaries(X, y)
    render_tree_diagram(X, y)
    print('Wrote decision_boundary.png, tree_diagram.png')


if __name__ == '__main__':
    main()
