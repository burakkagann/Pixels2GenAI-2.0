"""
random_forest.py - Compare a single decision tree against a Random
Forest on a noisy 2D dataset. The forest is far less wiggly because
it averages over many trees, each trained on a bootstrap sample with
a random feature subset.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

# ---------- CONFIG ----------
N_SAMPLES = 600
NOISE = 0.32
N_TREES = 80
MAX_DEPTH = None
RANDOM_STATE = 0
BG = '#0a0c18'
PALETTE = ['#ff7a90', '#80c6ff']
# ----------------------------


def render_two_panel():
    X, y = make_moons(n_samples=N_SAMPLES, noise=NOISE,
                      random_state=RANDOM_STATE)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.30, random_state=RANDOM_STATE
    )
    tree = DecisionTreeClassifier(max_depth=MAX_DEPTH,
                                  random_state=RANDOM_STATE).fit(X_tr, y_tr)
    forest = RandomForestClassifier(n_estimators=N_TREES,
                                    max_depth=MAX_DEPTH,
                                    random_state=RANDOM_STATE,
                                    n_jobs=-1).fit(X_tr, y_tr)

    xmin, xmax = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    ymin, ymax = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 240),
                         np.linspace(ymin, ymax, 240))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    fig, axes = plt.subplots(1, 2, figsize=(11, 5),
                             facecolor=BG, dpi=110)
    cmap = matplotlib.colors.ListedColormap(PALETTE)

    for ax, model, name in [
        (axes[0], tree, 'Single decision tree'),
        (axes[1], forest, f'Random Forest · {N_TREES} trees'),
    ]:
        ax.set_facecolor(BG)
        zz = model.predict_proba(grid)[:, 1].reshape(xx.shape)
        ax.contourf(xx, yy, zz, levels=20, alpha=0.5,
                    cmap=matplotlib.colormaps['coolwarm'])
        for cls in (0, 1):
            mask_tr = y_tr == cls
            ax.scatter(X_tr[mask_tr, 0], X_tr[mask_tr, 1], s=20,
                       c=PALETTE[cls], edgecolors='white', linewidths=0.4)
        train_acc = model.score(X_tr, y_tr)
        test_acc = model.score(X_te, y_te)
        ax.set_title(f'{name}\ntrain {train_acc:.2f} · test {test_acc:.2f}',
                     color='#dde2ee', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('forest_vs_tree.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_feature_importance():
    rng = np.random.default_rng(RANDOM_STATE)
    n, d = 1000, 8
    X = rng.normal(size=(n, d))
    # only features 0, 1, 5 matter
    y = ((X[:, 0] + X[:, 1] * 0.7 + np.sin(X[:, 5] * 2)) > 0).astype(int)

    forest = RandomForestClassifier(n_estimators=200,
                                    random_state=RANDOM_STATE,
                                    n_jobs=-1).fit(X, y)
    importance = forest.feature_importances_

    fig, ax = plt.subplots(figsize=(7, 4), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    bars = ax.bar(range(d), importance, color='#80c6ff',
                  edgecolor='white', linewidth=0.5)
    for i in (0, 1, 5):
        bars[i].set_color('#ff7a90')
    ax.set_xticks(range(d))
    ax.set_xticklabels([f'f{i}' for i in range(d)], color='#dde2ee')
    ax.set_yticks([])
    ax.set_title('Random Forest feature importances\n(true informative: f0, f1, f5)',
                 color='#dde2ee', fontsize=10)
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('feature_importance.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    render_two_panel()
    render_feature_importance()
    print('Wrote forest_vs_tree.png, feature_importance.png')


if __name__ == '__main__':
    main()
