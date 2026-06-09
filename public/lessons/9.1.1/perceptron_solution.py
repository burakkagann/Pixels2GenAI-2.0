import numpy as np

class Perceptron:
    def __init__(self, input_size, learning_rate=0.1):
        # Small random weights break symmetry so each input starts
        # with a different influence on the output
        self.weights = np.random.randn(input_size) * 0.01

        # Bias starts at zero; training will shift the decision
        # boundary away from the origin as needed
        self.bias = 0.0

        # Learning rate scales the size of each weight update
        self.learning_rate = learning_rate

    def forward(self, x):
        # Compute the weighted sum:  w1*x1 + w2*x2 + ... + b
        weighted_sum = np.dot(self.weights, x) + self.bias

        # Step activation: return 1 if non-negative, else 0
        return 1 if weighted_sum >= 0 else 0

    def train(self, X, y, epochs=100):
        # Iterate over the full dataset up to 'epochs' times
        for epoch in range(epochs):
            errors = 0

            # Process each sample individually (online learning)
            for i in range(len(X)):
                y_pred = self.forward(X[i])

                # Error: +1 if under-predicted, -1 if over-predicted, 0 if correct
                error = y[i] - y_pred

                if error != 0:
                    # Perceptron learning rule: adjust weights in
                    # the direction that reduces the error
                    self.weights += self.learning_rate * error * X[i]
                    self.bias += self.learning_rate * error
                    errors += 1

            # Early stop when all samples are classified correctly
            if errors == 0:
                print(f"Converged in {epoch + 1} epochs")
                return

        print(f"Training completed after {epochs} epochs")
