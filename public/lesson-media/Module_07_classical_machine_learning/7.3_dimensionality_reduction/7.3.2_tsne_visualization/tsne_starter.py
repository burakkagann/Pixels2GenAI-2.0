"""
tsne_starter.py - Implement the heavy-tailed similarity computation
that gives t-SNE its name.

Pixels2GenAI Project
"""

import numpy as np


def joint_q_probabilities(Y):
    """TODO: in the low-dimensional embedding Y (shape (n, 2)), compute
    the n x n matrix of pairwise affinities using the Student-t kernel
    with 1 degree of freedom:

        q_ij = (1 + |y_i - y_j|^2)^(-1) / sum over k != l of (1 + |y_k - y_l|^2)^(-1)

    With q_ii = 0.

    Hint: distances = pairwise squared L2 distances; (1+d)^(-1); zero
    the diagonal; divide by the total.
    """
    return np.zeros((len(Y), len(Y)))


def main():
    rng = np.random.default_rng(0)
    Y = rng.normal(size=(50, 2))
    Q = joint_q_probabilities(Y)
    print(f'Q shape: {Q.shape}')
    print(f'Q sum: {Q.sum():.4f}  (should be ~1.0 once implemented)')


if __name__ == '__main__':
    main()
