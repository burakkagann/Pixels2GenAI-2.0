"""
umap_starter.py - Build the kNN graph that underlies both UMAP and
Isomap. Once you have the graph, the rest is sparse matrix algebra.

Pixels2GenAI Project
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors


def knn_graph(X, k):
    """TODO: return the k-nearest-neighbour adjacency matrix.

    1. Use sklearn.neighbors.NearestNeighbors(n_neighbors=k+1) so each
       point's nearest neighbour is itself (which we discard).
    2. fit on X, then kneighbors(X) returns (distances, indices).
    3. Return: (indices, distances), shape (n, k) each, where indices[i, j]
       is the j-th nearest neighbour of point i and distances[i, j] is the
       corresponding distance.
    """
    return None, None


def main():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, 5))
    idx, dist = knn_graph(X, k=4)
    print(f'idx shape: {None if idx is None else idx.shape}')
    print(f'dist shape: {None if dist is None else dist.shape}')


if __name__ == '__main__':
    main()
