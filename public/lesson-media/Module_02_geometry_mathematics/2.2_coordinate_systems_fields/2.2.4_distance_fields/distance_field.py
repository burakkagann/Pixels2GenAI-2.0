"""
distance_field.py — generates the figure shown in the landing-page lesson preview.

Mirrors the code displayed in the Contents section of the Pixels2GenAI v2
landing (Module 2 · 2.2.4 Distance Fields). The only difference from the
displayed snippet is that this writes the figure to PNG instead of calling
plt.show(), so the result can be served as a static asset.
"""

import numpy as np
import matplotlib.pyplot as plt

N = 400
y, x = np.indices((N, N)) - N // 2

# Euclidean distance from center.
r = np.sqrt(x**2 + y**2)

# Sinusoid across distance.
field = np.cos(r * 0.25)

fig, ax = plt.subplots(figsize=(5, 5), dpi=120)
ax.imshow(field, cmap='twilight')
ax.axis('off')
fig.savefig('distance_field.png', bbox_inches='tight', pad_inches=0)
