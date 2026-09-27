import numpy as np
import matplotlib.pyplot as plt

class Perceptron:
    def __init__(self, n_in):
        self.w = np.zeros(n_in)
        self.b = 0.0

    def forward(self, x):
        return 1 if np.dot(self.w, x) + self.b >= 0 else 0

    def update(self, x, y, lr=0.1):
        pred = self.forward(x)
        err = y - pred
        self.w += lr * err * x
        self.b += lr * err

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([0, 1, 1, 0])

p = Perceptron(2)
# TODO: train for 1000 epochs, shuffling each epoch.
# TODO: plot data points and the (failed) decision line.
