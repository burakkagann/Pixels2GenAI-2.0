"""
The same picture made twice: once from a rule a person wrote, once from a rule
the program worked out from thirty examples.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

SIZE = 256
EXAMPLE_COUNT = 30
random_numbers = np.random.default_rng(7)

# Every pixel's position, from 0 to 1 across and down the canvas.
axis = np.linspace(0, 1, SIZE)
grid_x, grid_y = np.meshgrid(axis, axis)

# ALGORITHM: a person writes the rule, and every pixel follows it.
rule_image = 170 * grid_x + 85 * grid_y

# EXAMPLES: thirty random pixels and the brightness each one should have.
# The learning step below sees only these, never the rule itself.
example_x = random_numbers.random(EXAMPLE_COUNT)
example_y = random_numbers.random(EXAMPLE_COUNT)
example_brightness = 170 * example_x + 85 * example_y

# MACHINE LEARNING: find the three numbers a, b, c for which
# a*x + b*y + c comes closest to the examples (the least-squares fit).
inputs = np.column_stack([example_x, example_y, np.ones(EXAMPLE_COUNT)])
weights = np.linalg.lstsq(inputs, example_brightness, rcond=None)[0]
learned_image = weights[0] * grid_x + weights[1] * grid_y + weights[2]

# Put the two pictures side by side, with a white gap between them.
gap = np.full((SIZE, 12), 255.0)
both = np.hstack([rule_image, gap, learned_image])
Image.fromarray(np.clip(both, 0, 255).astype(np.uint8)).save("rule_vs_learned.png")

print("The rule a person wrote: 170*x + 85*y + 0")
print(f"The rule it learned:     {weights[0]:.1f}*x + {weights[1]:.1f}*y + {weights[2]:.1f}")
print("Saved rule_vs_learned.png")
