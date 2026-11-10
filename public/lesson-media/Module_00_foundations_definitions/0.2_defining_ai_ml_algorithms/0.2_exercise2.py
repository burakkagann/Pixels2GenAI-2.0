"""
Change what the learner sees, and watch how good the learned rule gets.

Left: the true picture. Right: the picture learned from the examples.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

# ========== CONFIG: change these values ==========
EXAMPLE_COUNT = 30      # How many pixels the learner gets to see
NOISE = 0               # Random error added to each example's brightness
RULE_SHAPE = "tilted"   # The true picture: "tilted" or "circle"
# =================================================

SIZE = 256
random_numbers = np.random.default_rng(7)


def true_brightness(x, y):
    """The picture the examples come from."""
    if RULE_SHAPE == "circle":
        # 0.71 is about the distance from the centre to a corner, so corners reach full brightness.
        return 255 * np.hypot(x - 0.5, y - 0.5) / 0.71
    return 170 * x + 85 * y


axis = np.linspace(0, 1, SIZE)
grid_x, grid_y = np.meshgrid(axis, axis)
true_image = true_brightness(grid_x, grid_y)

# The examples: random pixels, with an error added to each brightness.
example_x = random_numbers.random(EXAMPLE_COUNT)
example_y = random_numbers.random(EXAMPLE_COUNT)
errors = random_numbers.normal(0, NOISE, EXAMPLE_COUNT)
example_brightness = true_brightness(example_x, example_y) + errors

# The learner can only ever produce a*x + b*y + c: a flat, tilted surface.
inputs = np.column_stack([example_x, example_y, np.ones(EXAMPLE_COUNT)])
weights = np.linalg.lstsq(inputs, example_brightness, rcond=None)[0]
learned_image = weights[0] * grid_x + weights[1] * grid_y + weights[2]

# Average miss per pixel, on the 0 to 255 brightness scale.
average_error = np.mean(np.abs(true_image - learned_image))

gap = np.full((SIZE, 12), 255.0)
both = np.hstack([true_image, gap, learned_image])
Image.fromarray(np.clip(both, 0, 255).astype(np.uint8)).save("what_it_learned.png")

print(f"Examples: {EXAMPLE_COUNT}, noise: {NOISE}, shape: {RULE_SHAPE}")
print(f"Average error: {average_error:.1f} out of 255")
print("Saved what_it_learned.png")
