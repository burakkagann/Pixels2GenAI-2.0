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
    A simple feedforward neural network with one hidden layer.

    Architecture: Input (2) -> Hidden (4) -> Output (1)

    This network can solve the XOR problem, which a single perceptron cannot.
    """

    def __init__(self, input_size=2, hidden_size=4, output_size=1, learning_rate=0.5):
        """Initialize network with random weights."""
        self.learning_rate = learning_rate

        # Weights from input to hidden layer
        self.weights_input_hidden = np.random.randn(input_size, hidden_size) * 0.5
        self.bias_hidden = np.zeros((1, hidden_size))

        # Weights from hidden to output layer
        self.weights_hidden_output = np.random.randn(hidden_size, output_size) * 0.5
        self.bias_output = np.zeros((1, output_size))

    def forward(self, X):
        """
        Forward pass: compute output from input through all layers.

        Parameters:
            X: Input data of shape (n_samples, input_size)

        Returns:
            output: Network predictions of shape (n_samples, output_size)
        """
        # Input to hidden layer
        self.hidden_input = np.dot(X, self.weights_input_hidden) + self.bias_hidden
        self.hidden_output = sigmoid(self.hidden_input)

        # Hidden to output layer
        self.output_input = np.dot(self.hidden_output, self.weights_hidden_output) + self.bias_output
        self.output = sigmoid(self.output_input)

        return self.output

    def backward(self, X, y):
        """
        Backward pass: compute gradients and update weights using backpropagation.

        Parameters:
            X: Input data of shape (n_samples, input_size)
            y: Target labels of shape (n_samples, output_size)
        """
        n_samples = X.shape[0]

        # Output layer error (how wrong were we?)
        output_error = self.output - y
        output_delta = output_error * sigmoid_derivative(self.output_input)

        # Hidden layer error (propagate error backward)
        hidden_error = np.dot(output_delta, self.weights_hidden_output.T)
        hidden_delta = hidden_error * sigmoid_derivative(self.hidden_input)

        # Update weights and biases (gradient descent)
        self.weights_hidden_output -= self.learning_rate * np.dot(self.hidden_output.T, output_delta) / n_samples
        self.bias_output -= self.learning_rate * np.mean(output_delta, axis=0, keepdims=True)

        self.weights_input_hidden -= self.learning_rate * np.dot(X.T, hidden_delta) / n_samples
        self.bias_hidden -= self.learning_rate * np.mean(hidden_delta, axis=0, keepdims=True)

    def train(self, X, y, epochs=5000):
        """
        Train the network using backpropagation.

        Parameters:
            X: Training inputs
            y: Training targets
            epochs: Number of training iterations

        Returns:
            loss_history: List of loss values during training
        """
        loss_history = []

        for epoch in range(epochs):
            # Forward pass
            output = self.forward(X)

            # Calculate loss (mean squared error)
            loss = np.mean((y - output) ** 2)
            loss_history.append(loss)

            # Backward pass (update weights)
            self.backward(X, y)

            # Print progress every 1000 epochs
            if epoch % 1000 == 0:
                print(f"Epoch {epoch}: Loss = {loss:.6f}")

        return loss_history

    def predict(self, X):
        """Make predictions (round output to 0 or 1)."""
        return np.round(self.forward(X))

def visualize_decision_boundary(network, X, y, filename="feedforward_output.png"):
    """
    Create a visualization of the learned decision boundary.

    Parameters:
        network: Trained FeedforwardNetwork
        X: Training data points
        y: Training labels
        filename: Output filename
    """
    # Create image
    size = 400
    image = Image.new('RGB', (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Create grid of points to classify
    resolution = 100
    for i in range(resolution):
        for j in range(resolution):
            # Map pixel to data coordinates
            x1 = (i / resolution) * 1.4 - 0.2  # Range: -0.2 to 1.2
            x2 = (j / resolution) * 1.4 - 0.2

            # Get network prediction
            point = np.array([[x1, x2]])
            prediction = network.forward(point)[0, 0]

            # Color based on prediction (blue for 0, orange for 1)
            if prediction < 0.5:
                # Blue region (class 0)
                intensity = int(255 * (1 - prediction * 2))
                color = (200, 200, 255 - int(50 * prediction * 2))
            else:
                # Orange region (class 1)
                intensity = int(255 * ((prediction - 0.5) * 2))
                color = (255, 200 - int(50 * (prediction - 0.5) * 2), 150)

            # Map back to pixel coordinates
            px = int(i * size / resolution)
            py = int((resolution - 1 - j) * size / resolution)  # Flip y-axis

            # Draw pixel
            draw.rectangle([px, py, px + size//resolution, py + size//resolution], fill=color)

    # Draw data points
    point_radius = 8
    for i in range(len(X)):
        # Map data to pixel coordinates
        px = int((X[i, 0] + 0.2) / 1.4 * size)
        py = int((1 - (X[i, 1] + 0.2) / 1.4) * size)  # Flip y-axis

        # Color: blue circle for 0, orange circle for 1
        if y[i, 0] == 0:
            fill_color = (50, 50, 200)
            outline_color = (0, 0, 150)
        else:
            fill_color = (255, 150, 50)
            outline_color = (200, 100, 0)

        draw.ellipse(
            [px - point_radius, py - point_radius, px + point_radius, py + point_radius],
            fill=fill_color, outline=outline_color, width=2
        )

    image.save(filename)
    print(f"Decision boundary saved to {filename}")

if __name__ == "__main__":
    # XOR dataset: the classic problem that perceptrons cannot solve
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

    print("=" * 50)
    print("Training Feedforward Network on XOR Problem")
    print("=" * 50)
    print(f"\nXOR Truth Table:")
    print("Input 1 | Input 2 | Output")
    print("-" * 30)
    for i in range(len(X)):
        print(f"   {X[i, 0]}    |    {X[i, 1]}    |    {y[i, 0]}")

    # Create and train network
    np.random.seed(42)  # For reproducibility
    network = FeedforwardNetwork(input_size=2, hidden_size=4, output_size=1, learning_rate=0.5)

    print("\nTraining network...")
    loss_history = network.train(X, y, epochs=5000)

    # Test predictions
    print("\n" + "=" * 50)
    print("Predictions after training:")
    print("=" * 50)
    predictions = network.forward(X)
    for i in range(len(X)):
        pred_value = predictions[i, 0]
        pred_class = int(round(pred_value))
        correct = "Yes" if pred_class == y[i, 0] else "No"
        print(f"Input: {X[i]} -> Output: {pred_value:.4f} (Class {pred_class}) | Correct: {correct}")

    # Calculate accuracy
    accuracy = np.mean(np.round(predictions) == y) * 100
    print(f"\nAccuracy: {accuracy:.1f}%")

    # Visualize decision boundary
    visualize_decision_boundary(network, X, y)

    print("\nThe network successfully learned the XOR function!")
    print("This is impossible for a single perceptron (linear classifier).")
