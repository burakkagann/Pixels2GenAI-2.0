
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Create gradient variations (all 200x200 for comparison)
size = 200

# 1. Horizontal gradient (values change across columns)
horizontal = np.tile(np.linspace(0, 255, size, dtype=np.uint8), (size, 1))

# 2. Vertical gradient (values change across rows)
vertical = np.tile(np.linspace(0, 255, size, dtype=np.uint8).reshape(-1, 1), (1, size))

# 3. Diagonal gradient (average of horizontal and vertical)
h_component = np.linspace(0, 255, size)
v_component = np.linspace(0, 255, size).reshape(-1, 1)
diagonal = ((h_component + v_component) / 2).astype(np.uint8)

# 4. Reverse diagonal (opposite corners)
h_rev = np.linspace(255, 0, size)
v_component2 = np.linspace(0, 255, size).reshape(-1, 1)
diagonal_reverse = ((h_rev + v_component2) / 2).astype(np.uint8)

# Create matplotlib figure
fig, axes = plt.subplots(2, 2, figsize=(8, 8))

variations = [
    (horizontal, 'Horizontal Gradient\n(values vary by column)'),
    (vertical, 'Vertical Gradient\n(values vary by row)'),
    (diagonal, 'Diagonal Gradient\n(top-left to bottom-right)'),
    (diagonal_reverse, 'Reverse Diagonal\n(top-right to bottom-left)')
]

for ax, (img, title) in zip(axes.flatten(), variations):
    ax.imshow(img, cmap='gray', vmin=0, vmax=255)
    ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
    ax.axis('off')

plt.suptitle('Gradient Directions: How Coordinate Mapping Affects Output',
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('gradient_variations.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

