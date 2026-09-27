import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# NumPy functions introduced in this script:
#
#   np.meshgrid(x, y)   — Create 2-D coordinate grids from two
#                          1-D arrays.  Returns two arrays: one
#                          with x-values repeated across rows,
#                          one with y-values repeated down columns.
#                          Used here to classify every pixel in
#                          the plot to shade the background.
#
#   array.reshape(shape) — Change the shape of an array without
#                          copying data.  (-1,) means "flatten to
#                          1-D"; (rows, cols) means a 2-D grid.
# ---------------------------------------------------------------

# =============================================
# CONFIG — Modify these values for each Goal
# =============================================
LEARNING_RATE = 0.1        # Step size for weight updates (try: 0.01, 0.5, 1.0)
CLUSTER_SPREAD = 0.5       # Standard deviation of each cluster (try: 0.3, 1.0, 1.5)
CLUSTER_DISTANCE = 1.0     # Half-distance between cluster centers (try: 0.3, 0.5, 2.0)
RANDOM_SEED = 42           # Random seed for reproducibility (try: 7, 123, 999)
# =============================================

np.random.seed(RANDOM_SEED)

class Perceptron:
    def __init__(self, input_size, learning_rate=0.1):
        self.weights = np.random.randn(input_size) * 0.01
        self.bias = 0.0
        self.learning_rate = learning_rate

    def forward(self, x):
        weighted_sum = np.dot(self.weights, x) + self.bias
        return 1 if weighted_sum >= 0 else 0

    def train(self, X, y, epochs=100):
        error_history = []
        for epoch in range(epochs):
            errors = 0
            for i in range(len(X)):
                y_pred = self.forward(X[i])
                error = y[i] - y_pred
                if error != 0:
                    self.weights += self.learning_rate * error * X[i]
                    self.bias += self.learning_rate * error
                    errors += 1
            error_history.append(errors)
            if errors == 0:
                print(f"Converged in {epoch + 1} epochs")
                return error_history
        print(f"Finished {epochs} epochs with {errors} errors remaining")
        return error_history

# ---------------------------------------------------------------------------
# Generate data using CONFIG values
# ---------------------------------------------------------------------------
class_0 = np.random.randn(50, 2) * CLUSTER_SPREAD + [-CLUSTER_DISTANCE, -CLUSTER_DISTANCE]
class_1 = np.random.randn(50, 2) * CLUSTER_SPREAD + [CLUSTER_DISTANCE, CLUSTER_DISTANCE]
X = np.vstack([class_0, class_1])
y = np.array([0] * 50 + [1] * 50)

# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------
perceptron = Perceptron(input_size=2, learning_rate=LEARNING_RATE)
error_history = perceptron.train(X, y, epochs=50)
print(f"Final weights: {perceptron.weights}")
print(f"Final bias:    {perceptron.bias}")

# ---------------------------------------------------------------------------
# Visualize: decision boundary (left) + error curve (right)
# ---------------------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=120)

# --- Left panel: decision boundary with shaded regions ---

# np.meshgrid creates a grid of coordinates covering the plot area
x_range = np.linspace(-4, 4, 200)
y_range = np.linspace(-4, 4, 200)
xx, yy = np.meshgrid(x_range, y_range)

# Classify every grid point to shade the background
# array.reshape(-1) flattens 2-D grid into 1-D for iteration
grid_points = np.c_[xx.reshape(-1), yy.reshape(-1)]
Z = np.array([perceptron.forward(p) for p in grid_points])
# array.reshape(rows, cols) restores the 2-D grid shape
Z = Z.reshape(xx.shape)

ax1.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], colors=['#FDDCCC', '#C8DDEE'], alpha=0.6)
ax1.scatter(class_0[:, 0], class_0[:, 1], c='#E07B54', label='Class 0',
            edgecolors='white', linewidth=0.5, s=50, zorder=3)
ax1.scatter(class_1[:, 0], class_1[:, 1], c='#5B8DBE', label='Class 1',
            edgecolors='white', linewidth=0.5, s=50, zorder=3)

w1, w2 = perceptron.weights
b = perceptron.bias
if abs(w2) > 1e-8:
    x_line = np.linspace(-4, 4, 200)
    y_line = -(w1 * x_line + b) / w2
    ax1.plot(x_line, y_line, 'k-', linewidth=2, label='Boundary')

ax1.set_xlabel('Feature 1', fontsize=10)
ax1.set_ylabel('Feature 2', fontsize=10)
ax1.set_title(f'LR={LEARNING_RATE}  spread={CLUSTER_SPREAD}  dist={CLUSTER_DISTANCE}',
              fontsize=11, fontweight='bold')
ax1.legend(fontsize=9)
ax1.set_xlim(-4, 4)
ax1.set_ylim(-4, 4)
ax1.grid(True, alpha=0.3)

# --- Right panel: error per epoch ---
ax2.plot(range(1, len(error_history) + 1), error_history, 'o-', color='#E07B54',
         markersize=4, linewidth=1.5)
ax2.set_xlabel('Epoch', fontsize=10)
ax2.set_ylabel('Misclassified points', fontsize=10)
ax2.set_title('Training Error Over Epochs', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exercise2_result.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved exercise2_result.png")
