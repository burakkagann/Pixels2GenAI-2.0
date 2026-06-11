"""
svm_style.py - Compare SVM kernels on a small 2D dataset. The decision
boundary shape is everything you need to understand the algorithm: linear
SVM is a straight cut, polynomial SVM is a smooth curve, RBF SVM is a
local bubble around training points.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_moons, make_circles

# ---------- CONFIG ----------
N_SAMPLES = 300
NOISE = 0.20
RANDOM_STATE = 0
BG = '#0a0c18'
PALETTE = ['#ff7a90', '#80c6ff']
# ----------------------------


def render_kernel_zoo():
    X, y = make_moons(n_samples=N_SAMPLES, noise=NOISE,
                      random_state=RANDOM_STATE)
    classifiers = [
        ('linear', SVC(kernel='linear', C=1.0)),
        ('poly · degree 3', SVC(kernel='poly', degree=3, C=1.0, gamma='scale')),
        ('rbf · γ scale', SVC(kernel='rbf', C=1.0, gamma='scale')),
        ('rbf · γ=10', SVC(kernel='rbf', C=1.0, gamma=10.0)),
    ]

    xmin, xmax = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    ymin, ymax = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 200),
                         np.linspace(ymin, ymax, 200))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    fig, axes = plt.subplots(2, 2, figsize=(10, 9),
                             facecolor=BG, dpi=110)

    for ax, (name, clf) in zip(axes.ravel(), classifiers):
        clf.fit(X, y)
        zz = clf.decision_function(grid).reshape(xx.shape)
        ax.set_facecolor(BG)
        ax.contourf(xx, yy, zz, levels=20, alpha=0.4,
                    cmap=matplotlib.colormaps['coolwarm'])
        ax.contour(xx, yy, zz, levels=[0],
                   colors='white', linewidths=1.4)
        for cls in (0, 1):
            mask = y == cls
            ax.scatter(X[mask, 0], X[mask, 1], s=20,
                       c=PALETTE[cls], edgecolors='white', linewidths=0.4)
        # highlight support vectors
        sv = clf.support_vectors_
        ax.scatter(sv[:, 0], sv[:, 1], s=110, facecolors='none',
                   edgecolors='#ffd366', linewidths=1.2)
        train_acc = clf.score(X, y)
        ax.set_title(f'{name} · acc {train_acc:.2f} · {len(sv)} SVs',
                     color='#dde2ee', fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('#3a4258')

    fig.tight_layout()
    fig.savefig('svm_kernel_zoo.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_circles_demo():
    X, y = make_circles(n_samples=N_SAMPLES, noise=0.10, factor=0.4,
                        random_state=RANDOM_STATE)
    clf = SVC(kernel='rbf', C=2.0, gamma='scale').fit(X, y)
    xmin, xmax = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    ymin, ymax = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 200),
                         np.linspace(ymin, ymax, 200))
    grid = np.column_stack([xx.ravel(), yy.ravel()])

    fig, ax = plt.subplots(figsize=(6, 5.5), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    zz = clf.decision_function(grid).reshape(xx.shape)
    ax.contourf(xx, yy, zz, levels=20, alpha=0.4,
                cmap=matplotlib.colormaps['coolwarm'])
    ax.contour(xx, yy, zz, levels=[0],
               colors='white', linewidths=1.4)
    for cls in (0, 1):
        mask = y == cls
        ax.scatter(X[mask, 0], X[mask, 1], s=22,
                   c=PALETTE[cls], edgecolors='white', linewidths=0.4)
    sv = clf.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], s=110, facecolors='none',
               edgecolors='#ffd366', linewidths=1.2)
    ax.set_title('RBF kernel on concentric circles',
                 color='#dde2ee', fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('svm_circles.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    render_kernel_zoo()
    render_circles_demo()
    print('Wrote svm_kernel_zoo.png, svm_circles.png')


if __name__ == '__main__':
    main()
