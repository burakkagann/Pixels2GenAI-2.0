import numpy as np

# Fixed seed so every run produces the same results
np.random.seed(42)

class Perceptron:
    def __init__(self, input_size, learning_rate=0.1):
        # Small random weights break symmetry so each input starts
        # with a different influence on the output
        self.weights = np.random.randn(input_size) * 0.01

        # Bias starts at zero; it shifts the decision boundary
        # away from the origin during training
        self.bias = 0.0

        # Learning rate controls how much weights change per update;
        # larger values learn faster but may overshoot
        self.learning_rate = learning_rate

    def forward(self, x):
        # Weighted sum: dot product of weights and inputs, plus bias
        # This computes  w1*x1 + w2*x2 + ... + wn*xn + b
        weighted_sum = np.dot(self.weights, x) + self.bias

        # Step activation: output 1 when the sum is non-negative,
        # otherwise output 0 (binary classification)
        return 1 if weighted_sum >= 0 else 0

    def train(self, X, y, epochs=100):
        # Repeat over the full dataset up to 'epochs' times
        for epoch in range(epochs):
            errors = 0

            # Present each training sample one at a time
            for i in range(len(X)):
                # Predict with current weights
                y_pred = self.forward(X[i])

                # Error is the difference between the true label and
                # the prediction: +1, 0, or -1
                error = y[i] - y_pred

                # Update weights only when the prediction is wrong
                if error != 0:
                    # Perceptron learning rule:
                    # nudge weights toward the correct answer
                    self.weights += self.learning_rate * error * X[i]
                    self.bias += self.learning_rate * error
                    errors += 1

            # If every sample was classified correctly, stop early
            if errors == 0:
                print(f"Converged in {epoch + 1} epochs")
                return

        print(f"Training completed after {epochs} epochs")

# ---------------------------------------------------------------------------
# Generate linearly separable data: two Gaussian clusters in 2-D
# ---------------------------------------------------------------------------

# Class 0: 50 points centered at (-1, -1), spread 0.5
class_0 = np.random.randn(50, 2) * 0.5 + [-1, -1]

# Class 1: 50 points centered at (1, 1), spread 0.5
class_1 = np.random.randn(50, 2) * 0.5 + [1, 1]

# Stack both clusters into a single array of 100 samples
X = np.vstack([class_0, class_1])

# Labels: first 50 are class 0, next 50 are class 1
y = np.array([0] * 50 + [1] * 50)

# ---------------------------------------------------------------------------
# Train and report
# ---------------------------------------------------------------------------
print("Training perceptron...")
perceptron = Perceptron(input_size=2, learning_rate=0.1)
perceptron.train(X, y)
print(f"Final weights: {perceptron.weights}")
print(f"Final bias: {perceptron.bias}")
