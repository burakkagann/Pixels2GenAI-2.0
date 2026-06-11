import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
        # np.dot computes the weighted sum: w1*x1 + w2*x2 + bias
        weighted_sum = np.dot(self.weights, x) + self.bias

        # Step activation: output 1 when the sum is non-negative,
        # otherwise output 0 (binary classification)
        return 1 if weighted_sum >= 0 else 0

    def train(self, X, y, epochs=100):
        for epoch in range(epochs):
            errors = 0
            for i in range(len(X)):
                y_pred = self.forward(X[i])
                error = y[i] - y_pred
                if error != 0:
                    self.weights += self.learning_rate * error * X[i]
                    self.bias += self.learning_rate * error
                    errors += 1
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

# np.vstack stacks both clusters into a single (100, 2) array
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
print(f"Final bias:    {perceptron.bias}")

# ---------------------------------------------------------------------------
# Visualize the decision boundary
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6, 6), dpi=120)

# Plot data points colored by class
ax.scatter(class_0[:, 0], class_0[:, 1], c='#E07B54', label='Class 0',
           edgecolors='white', linewidth=0.5, s=50, zorder=3)
ax.scatter(class_1[:, 0], class_1[:, 1], c='#5B8DBE', label='Class 1',
           edgecolors='white', linewidth=0.5, s=50, zorder=3)

# Draw the decision boundary: w1*x1 + w2*x2 + b = 0
# Rearranged: x2 = -(w1*x1 + b) / w2
w1, w2 = perceptron.weights
b = perceptron.bias

if abs(w2) > 1e-8:
    # np.linspace creates evenly spaced x values for the line
    x_line = np.linspace(-3, 3, 200)
    y_line = -(w1 * x_line + b) / w2
    ax.plot(x_line, y_line, 'k-', linewidth=2, label='Decision boundary')

ax.set_xlabel('Feature 1 (x1)', fontsize=11)
ax.set_ylabel('Feature 2 (x2)', fontsize=11)
ax.set_title('Perceptron Decision Boundary', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exercise1_result.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved exercise1_result.png")
