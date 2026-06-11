"""
pca_starter.py - Implement PCA from scratch via SVD.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def pca_from_scratch(X, n_components):
    """TODO: implement PCA via the centered SVD.

    1. Centre X by subtracting the column-mean.
    2. Apply np.linalg.svd(Xc, full_matrices=False) to get U, S, Vt.
       (Vt has shape (d, d); rows are the principal axes in descending order.)
    3. Project: scores = Xc @ Vt[:n_components].T
    4. Return (scores, principal_axes, explained_variance_ratio).
       explained_variance_ratio[i] = S[i]^2 / (S**2).sum() — share of total variance.
    """
    return None, None, None


def main():
    rng = np.random.default_rng(0)
    # 1000 points roughly on an ellipse rotated 30 degrees
    angle = np.deg2rad(30)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle), np.cos(angle)]])
    raw = rng.normal(0, 1.0, size=(1000, 2)) * np.array([3.0, 0.8])
    X = raw @ R.T

    scores, axes, var = pca_from_scratch(X, n_components=2)
    print(f'Explained variance: {var}')
    print(f'Principal axes (rows):\n{axes}')


if __name__ == '__main__':
    main()
