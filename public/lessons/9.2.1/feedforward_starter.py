import numpy as np
from PIL import Image, ImageDraw

def sigmoid(x):
    """Sigmoid activation function: maps any value to range (0, 1)."""
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

def sigmoid_derivative(x):
    """Derivative of sigmoid: used in backpropagation."""
    s = sigmoid(x)
    return s * (1 - s)

class FeedforwardNetwork:
    """
    A feedforward neural network with one hidden layer.

    Architecture: Input (2) -> Hidden (4) -> Output (1)
    """

    def __init__(self, input_size=2, hidden_size=4, output_size=1, learning_rate=0.5):
        """
        Initialize the network with random weights.

        TODO: Complete this method to initialize:
        - weights_input_hidden: weights from input to hidden layer
        - bias_hidden: biases for hidden layer
        - weights_hidden_output: weights from hidden to output layer
        - bias_output: bias for output layer
        """
        self.learning_rate = learning_rate

        # TODO: Initialize weights from input to hidden layer
        # Hint: Use np.random.randn(rows, cols) * 0.5 for weights
        # Shape should be (input_size, hidden_size)
        self.weights_input_hidden = None  # Replace this line

        # TODO: Initialize biases for hidden layer
        # Hint: Use np.zeros((1, hidden_size))
        self.bias_hidden = None  # Replace this line

        # TODO: Initialize weights from hidden to output layer
        # Shape should be (hidden_size, output_size)
        self.weights_hidden_output = None  # Replace this line

        # TODO: Initialize bias for output layer
        self.bias_output = None  # Replace this line

    def forward(self, X):
        """
        Forward pass: compute output from input through all layers.

        Parameters:
            X: Input data of shape (n_samples, input_size)

        Returns:
            output: Network predictions of shape (n_samples, output_size)

        TODO: Complete this method to compute:
        1. Hidden layer input (weighted sum of inputs + bias)
        2. Hidden layer output (apply sigmoid)
        3. Output layer input (weighted sum of hidden outputs + bias)
        4. Final output (apply sigmoid)
        """
        # TODO: Compute hidden layer input
        # Hint: Use np.dot(X, self.weights_input_hidden) + self.bias_hidden
        self.hidden_input = None  # Replace this line

        # TODO: Compute hidden layer output (apply sigmoid)
        self.hidden_output = None  # Replace this line

        # TODO: Compute output layer input
        self.output_input = None  # Replace this line

        # TODO: Compute final output (apply sigmoid)
        self.output = None  # Replace this line

        return self.output

    def backward(self, X, y):
        """
        Backward pass: compute gradients and update weights.

        Parameters:
            X: Input data
            y: Target labels

        TODO: Complete this method to:
        1. Calculate output layer error and delta
        2. Calculate hidden layer error and delta
        3. Update all weights and biases
        """
        n_samples = X.shape[0]

        # TODO: Calculate output error (prediction - target)
        output_error = None  # Replace this line

        # TODO: Calculate output delta (error * sigmoid_derivative)
        output_delta = None  # Replace this line

        # TODO: Calculate hidden layer error (backpropagate from output)
        # Hint: np.dot(output_delta, self.weights_hidden_output.T)
        hidden_error = None  # Replace this line

        # TODO: Calculate hidden delta
        hidden_delta = None  # Replace this line

        # TODO: Update weights and biases using gradient descent
        # Hint: weight -= learning_rate * gradient
        # self.weights_hidden_output -= ...
        # self.bias_output -= ...
        # self.weights_input_hidden -= ...
        # self.bias_hidden -= ...
        pass  # Replace with weight updates

    def train(self, X, y, epochs=5000):
        """Train the network using backpropagation."""
        loss_history = []

        for epoch in range(epochs):
            output = self.forward(X)
            loss = np.mean((y - output) ** 2)
            loss_history.append(loss)
            self.backward(X, y)

            if epoch % 1000 == 0:
                print(f"Epoch {epoch}: Loss = {loss:.6f}")

        return loss_history

    def predict(self, X):
        """Make predictions (round output to 0 or 1)."""
        return np.round(self.forward(X))

if __name__ == "__main__":
    # XOR dataset
    X = np.array([
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1]
    ])

    y = np.array([
        [0],  # 0 XOR 0 = 0
        [1],  # 0 XOR 1 = 1
        [1],  # 1 XOR 0 = 1
        [0]   # 1 XOR 1 = 0
    ])

    print("Training Feedforward Network on XOR Problem")
    print("=" * 50)

    np.random.seed(42)
    network = FeedforwardNetwork()

    # This will fail until you complete the TODO sections!
    try:
        loss_history = network.train(X, y, epochs=5000)

        print("\nPredictions after training:")
        print("-" * 30)
        predictions = network.forward(X)
        for i in range(len(X)):
            pred = predictions[i, 0]
            print(f"Input: {X[i]} -> Output: {pred:.4f} (Class {int(round(pred))})")

        accuracy = np.mean(np.round(predictions) == y) * 100
        print(f"\nAccuracy: {accuracy:.1f}%")

        if accuracy == 100:
            print("\nCongratulations! Your network learned XOR successfully!")
        else:
            print("\nKeep trying! Check your backward pass implementation.")

    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure you've completed all the TODO sections!")
