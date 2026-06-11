import numpy as np

# XOR dataset
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Initialize weights
np.random.seed(42)
W1 = np.random.randn(2, 4) * 0.5  # 2 inputs -> 4 hidden
W2 = np.random.randn(4, 1) * 0.5  # 4 hidden -> 1 output

learning_rate = 1.0

print("Training XOR with backpropagation...")
print("(Complete the TODOs to see learning happen!)")
print()

for epoch in range(1001):
    # =========================================================
    # FORWARD PASS (complete - do not modify)
    # =========================================================
    a1 = sigmoid(X @ W1)     # Hidden layer: shape (4, 4)
    a2 = sigmoid(a1 @ W2)    # Output layer: shape (4, 1)

    loss = np.mean((a2 - y) ** 2)

    # =========================================================
    # BACKWARD PASS (complete the TODOs below)
    # =========================================================

    # TODO 1: Compute output error
    # The error is simply: prediction - target
    # Formula: dz2 = a2 - y
    dz2 = None  # <-- Replace None with the correct formula

    # TODO 2: Compute gradient for W2
    # How much did each hidden neuron contribute to the error?
    # Formula: dW2 = a1.T @ dz2 / 4
    # (We divide by 4 because we have 4 training samples)
    dW2 = None  # <-- Replace None with the correct formula

    # TODO 3: Compute hidden layer error using chain rule
    # Error flows backward through W2, then through sigmoid derivative
    # Sigmoid derivative: a1 * (1 - a1)
    # Formula: dz1 = (dz2 @ W2.T) * (a1 * (1 - a1))
    dz1 = None  # <-- Replace None with the correct formula

    # TODO 4: Compute gradient for W1
    # Formula: dW1 = X.T @ dz1 / 4
    dW1 = None  # <-- Replace None with the correct formula

    # TODO 5: Update weights using gradient descent
    # Formula: W = W - learning_rate * gradient
    # Update both W1 and W2
    pass  # <-- Replace with weight updates

    # Print progress
    if epoch % 200 == 0:
        print(f"Epoch {epoch:4d}: Loss = {loss:.4f}")

# Final predictions
print()
print("Final predictions:")
for i in range(4):
    print(f"  {X[i]} -> {a2[i,0]:.3f} (target: {y[i,0]})")

# Check if learning worked
if loss < 0.01:
    print("\nSuccess! The network learned XOR.")
else:
    print("\nLoss is still high. Check your TODO implementations.")
