import numpy as np

# XOR dataset
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([[0], [1], [1], [0]])

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# Initialize weights
np.random.seed(42)
W1 = np.random.randn(2, 4) * 0.5
W2 = np.random.randn(4, 1) * 0.5

learning_rate = 1.0

print("Training XOR with backpropagation (Solution)...")
print()

for epoch in range(1001):
    # Forward pass
    a1 = sigmoid(X @ W1)
    a2 = sigmoid(a1 @ W2)

    loss = np.mean((a2 - y) ** 2)

    # Backward pass (all TODOs completed)
    dz2 = a2 - y                          # TODO 1: Output error
    dW2 = a1.T @ dz2 / 4                  # TODO 2: Gradient for W2
    dz1 = (dz2 @ W2.T) * (a1 * (1 - a1))  # TODO 3: Hidden error (chain rule)
    dW1 = X.T @ dz1 / 4                   # TODO 4: Gradient for W1

    # TODO 5: Weight updates
    W1 -= learning_rate * dW1
    W2 -= learning_rate * dW2

    if epoch % 200 == 0:
        print(f"Epoch {epoch:4d}: Loss = {loss:.4f}")

print()
print("Final predictions:")
for i in range(4):
    status = "Correct!" if abs(a2[i, 0] - y[i, 0]) < 0.1 else ""
    print(f"  {X[i]} -> {a2[i,0]:.3f} (target: {y[i,0]}) {status}")

print()
print("Success! The network learned XOR using backpropagation.")
