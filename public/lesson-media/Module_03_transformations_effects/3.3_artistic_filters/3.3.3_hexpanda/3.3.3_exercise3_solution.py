import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

H, W = 200, 200

row, col = np.indices((H, W))
gradient = ((row + col) / ((H - 1) + (W - 1)) * 255).astype(np.uint8)

df = pd.DataFrame(gradient).unstack().reset_index()
df.columns = ['x', 'y', 'intensity']
df['y'] = -df['y']

sample = df.sample(len(df) // 2, random_state=42)

fig, ax = plt.subplots(figsize=(8, 8))
sample.plot.hexbin(x='x', y='y', gridsize=25, cmap='viridis', ax=ax)
ax.set_aspect('equal'); ax.axis('off')
plt.savefig('gradient_hexbin.png', bbox_inches='tight', dpi=120)
