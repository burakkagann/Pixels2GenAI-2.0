import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import imageio.v2 as imageio

# =====================================================================
# PASTE YOUR PERCEPTRON CLASS FROM EXERCISE 3 BELOW
# (or use this reference implementation)
# =====================================================================

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
                return error_history
        return error_history

# =====================================================================
# CONFIG — Change these to create different compositions
# =====================================================================
CANVAS_SIZE = 400            # Width and height in pixels
NUM_PERCEPTRONS = 4          # More perceptrons = more regions (2^N colors)
POINTS_PER_CLASS = 30        # Training points per class per perceptron
SPREAD = 0.4                 # Cluster spread (smaller = easier to learn)
TRAINING_EPOCHS = 20         # Maximum frames in the animation
LEARNING_RATE = 0.05         # Small LR = slower convergence = more frames
RANDOM_SEED = 42             # Change for different compositions
FPS = 3                      # Animation speed (frames per second)
# =====================================================================

# =====================================================================
# TRAINING DATA — Each entry defines one perceptron's training task.
# The two centers determine the angle of the learned boundary.
#
#   (center_class_0, center_class_1)
#
# Try changing the centers to tilt boundaries differently!
# =====================================================================
BOUNDARY_CONFIGS = [
    ([-1.0,  0.0], [ 1.0, 0.0]),   # Roughly vertical boundary
    ([ 0.0, -1.0], [ 0.0, 1.0]),   # Roughly horizontal boundary
    ([-1.0, -1.0], [ 1.0, 1.0]),   # Diagonal boundary (/)
    ([-1.0,  1.0], [ 1.0, -1.0]),  # Anti-diagonal boundary (\)
]
# =====================================================================

np.random.seed(RANDOM_SEED)

# --- Color palette: distinct colors for each region ---
num_regions = 2 ** NUM_PERCEPTRONS
# np.linspace creates evenly spaced hue values across [0, 1]
hues = np.linspace(0, 1, num_regions, endpoint=False)
palette = np.zeros((num_regions, 3), dtype=np.uint8)
for i, h in enumerate(hues):
    # Convert HSV to RGB using matplotlib's colormap
    r, g, b, _ = plt.cm.Set3(h)
    palette[i] = [int(r * 255), int(g * 255), int(b * 255)]

def train_one_epoch(perceptron, X, y):
    """Train for exactly one epoch, recording errors."""
    errors = 0
    for i in range(len(X)):
        y_pred = perceptron.forward(X[i])
        error = y[i] - y_pred
        if error != 0:
            perceptron.weights += perceptron.learning_rate * error * X[i]
            perceptron.bias += perceptron.learning_rate * error
            errors += 1
    return errors

def render_canvas(perceptrons, size):
    """Render the canvas using vectorized operations for speed.

    np.meshgrid creates coordinate grids so we can classify all
    pixels at once instead of looping pixel by pixel.
    """
    # Create normalized coordinate grids: [-2, 2] range
    xs = np.linspace(-2, 2, size)
    ys = np.linspace(-2, 2, size)
    xx, yy = np.meshgrid(xs, ys)

    # Compute binary signature for every pixel simultaneously
    signature = np.zeros((size, size), dtype=int)
    for i, p in enumerate(perceptrons):
        # Vectorized forward pass: z = w1*x + w2*y + b
        z = xx * p.weights[0] + yy * p.weights[1] + p.bias
        # Step activation: 1 where z >= 0, else 0
        signature += (z >= 0).astype(int) * (2 ** i)

    # Map signatures to colors
    canvas = palette[signature]
    return canvas

# --- Create perceptrons and training data ---
perceptrons = []
datasets = []

for idx in range(NUM_PERCEPTRONS):
    p = Perceptron(input_size=2, learning_rate=LEARNING_RATE)
    perceptrons.append(p)

    # Use config if available, otherwise generate random centers
    if idx < len(BOUNDARY_CONFIGS):
        c0, c1 = BOUNDARY_CONFIGS[idx]
    else:
        angle = np.random.uniform(0, 2 * np.pi)
        c0 = [-np.cos(angle), -np.sin(angle)]
        c1 = [np.cos(angle), np.sin(angle)]

    # np.random.randn generates training points around each center
    class_0 = np.random.randn(POINTS_PER_CLASS, 2) * SPREAD + c0
    class_1 = np.random.randn(POINTS_PER_CLASS, 2) * SPREAD + c1
    X = np.vstack([class_0, class_1])
    y_labels = np.array([0] * POINTS_PER_CLASS + [1] * POINTS_PER_CLASS)
    datasets.append((X, y_labels))

# --- Train and render frames ---
print("Rendering evolving art...")
frames = []

# Frame 0: initial random weights (before any training)
frame = render_canvas(perceptrons, CANVAS_SIZE)
frames.append(frame)

for epoch in range(TRAINING_EPOCHS):
    # Train each perceptron for one epoch
    total_errors = 0
    for p, (X, y_labels) in zip(perceptrons, datasets):
        errors = train_one_epoch(p, X, y_labels)
        total_errors += errors

    # Render the canvas with current weights
    frame = render_canvas(perceptrons, CANVAS_SIZE)
    frames.append(frame)

    status = "converged" if total_errors == 0 else f"{total_errors} errors"
    print(f"  Epoch {epoch + 1:2d}: {status}")

    if total_errors == 0:
        # All perceptrons converged — add a few duplicate frames
        # so the final composition holds on screen
        for _ in range(4):
            frames.append(frame)
        break

# --- Save animated GIF ---
imageio.mimsave('evolving_art.gif', frames, fps=FPS, loop=0)
print(f"Saved evolving_art.gif ({len(frames)} frames at {FPS} fps)")

# --- Also save the final frame as a static image ---
Image.fromarray(frames[-1]).save('evolving_art_final.png')
print("Saved evolving_art_final.png")
