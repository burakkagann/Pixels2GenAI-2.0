import numpy as np

# XOR dataset: outputs 1 when inputs differ, 0 when they match
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

def sigmoid(z):
    """Squash any value to range (0, 1)."""
    return 1 / (1 + np.exp(-z))

# Initialize network: 2 inputs -> 4 hidden -> 1 output
np.random.seed(42)
W1 = np.random.randn(2, 4) * 0.5  # Input to hidden weights
W2 = np.random.randn(4, 1) * 0.5  # Hidden to output weights
learning_rate = 1.0

print("XOR Problem - The Challenge That Needs Hidden Layers")
print("=" * 55)
print("Truth Table: XOR outputs 1 when inputs DIFFER")
print("  [0,0] -> 0    [0,1] -> 1    [1,0] -> 1    [1,1] -> 0")
print()
print("Training network with backpropagation...")
print()

# Training loop with backpropagation
for epoch in range(2001):
    # Forward pass: compute predictions
    a1 = sigmoid(X @ W1)      # Hidden layer activations
    a2 = sigmoid(a1 @ W2)     # Output predictions

    # Compute loss (mean squared error)
    loss = np.mean((a2 - y) ** 2)

    # Backward pass: compute gradients using chain rule
    dz2 = a2 - y                          # Output error
    dW2 = a1.T @ dz2 / 4                  # Gradient for W2
    dz1 = (dz2 @ W2.T) * (a1 * (1 - a1))  # Hidden error (chain rule)
    dW1 = X.T @ dz1 / 4                   # Gradient for W1

    # Update weights (gradient descent)
    W2 -= learning_rate * dW2
    W1 -= learning_rate * dW1

    # Print progress every 500 epochs
    if epoch % 500 == 0:
        preds = [f"{a2[i,0]:.2f}" for i in range(4)]
        print(f"Epoch {epoch:4d}: Loss = {loss:.4f}  Predictions: {preds}")

# Final results
print()
print("Final Results:")
print("-" * 45)
for i in range(4):
    pred = a2[i, 0]
    target = y[i, 0]
    status = "Correct!" if abs(pred - target) < 0.1 else "Wrong"
    print(f"  Input {X[i]} -> {pred:.3f} (target: {target}) {status}")
