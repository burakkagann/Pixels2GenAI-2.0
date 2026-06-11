"""
forest_starter.py - Implement bagging from scratch on top of sklearn's
DecisionTreeClassifier. The "forest" reduces variance by averaging
predictions from many trees trained on bootstrap samples.

Pixels2GenAI Project
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

N_TREES = 50
MAX_DEPTH = None
RANDOM_STATE = 0


class BaggedForest:
    """TODO: implement a bagging ensemble.

    fit(X, y):
      For tree_i in range(n_trees):
        Sample n rows from X with replacement → X_boot, y_boot.
        Optionally sample a random feature subset of size sqrt(n_features).
        Fit a DecisionTreeClassifier on the bootstrap sample.
        Store the tree (and which feature columns it used).

    predict(X):
      For each tree, predict on X using its feature columns.
      Return the majority-vote (or mean predict_proba and argmax).
    """

    def __init__(self, n_trees, max_depth, random_state):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.random_state = random_state
        self.trees = []
        self.feature_subsets = []

    def fit(self, X, y):
        pass  # TODO

    def predict(self, X):
        return np.zeros(len(X), dtype=int)


def main():
    X, y = make_moons(n_samples=500, noise=0.30, random_state=RANDOM_STATE)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.30,
                                              random_state=RANDOM_STATE)
    forest = BaggedForest(N_TREES, MAX_DEPTH, RANDOM_STATE).fit(X_tr, y_tr)
    preds = forest.predict(X_te)
    acc = (preds == y_te).mean()
    print(f'BaggedForest test accuracy: {acc:.2f}')


if __name__ == '__main__':
    main()
