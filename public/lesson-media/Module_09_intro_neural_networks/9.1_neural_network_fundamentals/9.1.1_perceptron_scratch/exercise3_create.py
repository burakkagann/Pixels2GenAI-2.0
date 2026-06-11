import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# NumPy functions you will use in the TODOs:
#
#   np.random.randn(n)  — Draw n random numbers from a standard
#                          normal distribution (bell curve, mean=0,
#                          std=1).  We multiply by 0.01 to get
#                          small initial weights.
#
#   np.dot(a, b)        — Dot product of two arrays.  For vectors
#                          a=[a1,a2] and b=[b1,b2] this returns
#                          a1*b1 + a2*b2.  This is the "weighted
#                          sum" at the heart of the perceptron.
# ---------------------------------------------------------------

class Perceptron:
    def __init__(self, input_size, learning_rate=0.1):
        # TODO 1: Initialize weights, bias, and learning rate.
    
        self.weights = None       # Replace
        self.bias = None          # Replace
        self.learning_rate = None # Replace

    def forward(self, x):
        # TODO 2: Compute the perceptron output.
        #
        #   Step A: 
        #   Step B: 
        #
        weighted_sum = None  # Replace (Step A)
        pass                 # Replace (Step B)

    def train(self, X, y, epochs=100):
        error_history = []
        for epoch in range(epochs):
            errors = 0
            for i in range(len(X)):
                # TODO 3: Predict, compute error, update if wrong.
                #
                #  
                #   
                #
                #   
                #       
                #      
                #      
                pass  # Replace with prediction + update logic

            error_history.append(errors)
            if errors == 0:
                print(f"Converged in {epoch + 1} epochs")
                return error_history
        print(f"Training completed after {epochs} epochs")
        return error_history

# =====================================================================
# Everything below is PROVIDED — do not edit until TODOs are complete.
# After your perceptron works, feel free to change the CONFIG values.
# =====================================================================

# CONFIG — experiment with these after completing the TODOs
RANDOM_SEED = 42
LEARNING_RATE = 0.1
NUM_POINTS = 50

np.random.seed(RANDOM_SEED)

# Generate two clusters
class_0 = np.random.randn(NUM_POINTS, 2) * 0.5 + [-1, -1]
class_1 = np.random.randn(NUM_POINTS, 2) * 0.5 + [1, 1]
X = np.vstack([class_0, class_1])
y = np.array([0] * NUM_POINTS + [1] * NUM_POINTS)

# Train
perceptron = Perceptron(input_size=2, learning_rate=LEARNING_RATE)
error_history = perceptron.train(X, y)
print(f"Final weights: {perceptron.weights}")
print(f"Final bias:    {perceptron.bias}")

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=120)

# Left: decision boundary
x_range = np.linspace(-3, 3, 200)
y_range = np.linspace(-3, 3, 200)
xx, yy = np.meshgrid(x_range, y_range)
grid_points = np.c_[xx.reshape(-1), yy.reshape(-1)]
Z = np.array([perceptron.forward(p) for p in grid_points])
Z = Z.reshape(xx.shape)

ax1.contourf(xx, yy, Z, levels=[-0.5, 0.5, 1.5], colors=['#FDDCCC', '#C8DDEE'], alpha=0.6)
ax1.scatter(class_0[:, 0], class_0[:, 1], c='#E07B54', label='Class 0',
            edgecolors='white', linewidth=0.5, s=50, zorder=3)
ax1.scatter(class_1[:, 0], class_1[:, 1], c='#5B8DBE', label='Class 1',
            edgecolors='white', linewidth=0.5, s=50, zorder=3)

w1, w2 = perceptron.weights
b = perceptron.bias
if abs(w2) > 1e-8:
    x_line = np.linspace(-3, 3, 200)
    y_line = -(w1 * x_line + b) / w2
    ax1.plot(x_line, y_line, 'k-', linewidth=2, label='Boundary')

ax1.set_xlabel('Feature 1', fontsize=10)
ax1.set_ylabel('Feature 2', fontsize=10)
ax1.set_title('Your Perceptron Decision Boundary', fontsize=11, fontweight='bold')
ax1.legend(fontsize=9)
ax1.set_xlim(-3, 3)
ax1.set_ylim(-3, 3)
ax1.grid(True, alpha=0.3)

# Right: error curve
ax2.plot(range(1, len(error_history) + 1), error_history, 'o-', color='#E07B54',
         markersize=4, linewidth=1.5)
ax2.set_xlabel('Epoch', fontsize=10)
ax2.set_ylabel('Misclassified points', fontsize=10)
ax2.set_title('Training Error Over Epochs', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('exercise3_result.png', dpi=120, bbox_inches='tight')
plt.close()
print("Saved exercise3_result.png")

# ---------------------------------------------------------
# MAKE IT YOUR OWN (after completing the TODOs above):
#
#   - Change LEARNING_RATE to 0.01 or 1.0 and compare
#   - Change NUM_POINTS to 200 for denser clusters
#   - Try RANDOM_SEED = 7 for a different data layout
#   - Add a third cluster and see what happens
# ---------------------------------------------------------
