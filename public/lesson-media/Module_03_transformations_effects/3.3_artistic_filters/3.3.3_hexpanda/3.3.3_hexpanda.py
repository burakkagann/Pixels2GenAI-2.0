import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Grayscale + invert so dark → high value
pixels = np.array(Image.open('panda.png').convert('L'))
inverted = 255 - pixels

# Pixel grid → long-format DataFrame (x, y, intensity)
df = pd.DataFrame(inverted).unstack()             # (x, y) → intensity Series
df = df[df > 0].reset_index()                     # drop background, become flat
df.columns = ['x', 'y', 'intensity']
df['y'] = -df['y']                                # flip to maths y-up

# Sample 25% for an airier mosaic, then hexbin
sample = df.sample(len(df) // 4, random_state=0)

fig, ax = plt.subplots(figsize=(8, 8))
sample.plot.hexbin(x='x', y='y', gridsize=30, cmap='Greys', ax=ax)
ax.set_aspect('equal'); ax.axis('off')
plt.tight_layout()
plt.savefig('hexpanda.png', dpi=150, bbox_inches='tight', facecolor='white')
