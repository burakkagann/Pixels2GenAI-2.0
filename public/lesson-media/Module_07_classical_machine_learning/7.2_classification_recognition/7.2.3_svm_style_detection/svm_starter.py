"""
svm_starter.py - Implement the RBF kernel matrix from scratch.

Once you have K, sklearn can fit an SVM in *precomputed-kernel* mode.
This lets you focus on the kernel-trick idea without re-implementing
the quadratic-program solver.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.datasets import make_moons


def rbf_kernel(X1, X2, gamma):
    """TODO: compute the RBF (Gaussian) kernel matrix.

    K[i, j] = exp(-gamma * |X1[i] - X2[j]|^2)

    Use NumPy broadcasting. Output shape: (len(X1), len(X2)).
    """
    return np.zeros((len(X1), len(X2)))


def main():
    X, y = make_moons(n_samples=300, noise=0.20, random_state=0)
    gamma = 1.5

    K_train = rbf_kernel(X, X, gamma)
    clf = SVC(kernel='precomputed', C=1.0).fit(K_train, y)

    # decision boundary
    xmin, xmax = X[:, 0].min() - 0.4, X[:, 0].max() + 0.4
    ymin, ymax = X[:, 1].min() - 0.4, X[:, 1].max() + 0.4
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 200),
                         np.linspace(ymin, ymax, 200))
    grid = np.column_stack([xx.ravel(), yy.ravel()])
    K_test = rbf_kernel(grid, X, gamma)
    zz = clf.decision_function(K_test).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(6, 5.5), facecolor='#0a0c18', dpi=110)
    ax.set_facecolor('#0a0c18')
    ax.contourf(xx, yy, zz, levels=20, alpha=0.4,
                cmap=matplotlib.colormaps['coolwarm'])
    ax.contour(xx, yy, zz, levels=[0], colors='white', linewidths=1.3)
    palette = ['#ff7a90', '#80c6ff']
    for cls in (0, 1):
        mask = y == cls
        ax.scatter(X[mask, 0], X[mask, 1], s=22,
                   c=palette[cls], edgecolors='white', linewidths=0.4)
    ax.set_xticks([]); ax.set_yticks([])
    fig.tight_layout()
    fig.savefig('svm_starter.png', facecolor='#0a0c18', dpi=110)
    print(f'Train accuracy: {clf.score(K_train, y):.2f}')


if __name__ == '__main__':
    main()
