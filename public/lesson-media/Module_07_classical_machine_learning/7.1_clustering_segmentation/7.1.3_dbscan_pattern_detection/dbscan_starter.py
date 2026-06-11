"""
dbscan_starter.py - Implement DBSCAN from scratch.

The data generation and rendering are wired up. You implement
`dbscan_fit()` core: BFS expansion from each unvisited core point,
labelling reachable neighbours, and marking the rest as noise.

Pixels2GenAI Project
"""

import numpy as np
from sklearn.datasets import make_moons


EPS = 0.20
MIN_SAMPLES = 7


def dbscan_fit(X, eps, min_samples):
    """TODO: implement DBSCAN.

    For every unvisited point p:
      neighbours_p = points within `eps` of p (Euclidean)
      if |neighbours_p| < min_samples:
        label p as -1 (noise) for now (may be revisited as a border point)
        continue
      otherwise p is a CORE point — start a new cluster
      BFS: extend the cluster by adding every neighbour q;
           if q is itself a core point, add q's neighbours too;
           border points (in cluster but not core) stop the BFS.

    Return labels: array of length n, -1 for noise, 0..k-1 for clusters.
    """
    return np.full(len(X), -1, dtype=int)


def main():
    X, _ = make_moons(n_samples=300, noise=0.08, random_state=0)
    labels = dbscan_fit(X, EPS, MIN_SAMPLES)
    n_clusters = len(set(labels) - {-1})
    n_noise = int(np.sum(labels == -1))
    print(f'Found {n_clusters} clusters, {n_noise} noise points')


if __name__ == '__main__':
    main()
