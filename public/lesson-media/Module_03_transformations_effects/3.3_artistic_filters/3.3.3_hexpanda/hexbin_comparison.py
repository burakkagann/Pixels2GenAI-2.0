import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Load and prepare the image
panda_image = Image.open('panda.png')
panda_grayscale = panda_image.convert('L')
pixel_array = np.array(panda_grayscale)

# Invert colors for hexbin density
inverted_pixels = 255 - pixel_array

# Convert to DataFrame format
pixel_dataframe = pd.DataFrame(inverted_pixels)
pixel_series = pixel_dataframe.unstack()
foreground_pixels = pixel_series[pixel_series > 0]
pixel_data = foreground_pixels.reset_index()
pixel_data.columns = ['x', 'y', 'intensity']
pixel_data['y'] = -pixel_data['y']

# Sample the data
sampled_data = pixel_data.sample(len(pixel_data) // 4, random_state=42)

# Grid sizes to compare
grid_sizes = [15, 30, 50, 80]
titles = [
    'Grid Size: 15 (Very Abstract)',
    'Grid Size: 30 (Balanced)',
    'Grid Size: 50 (More Detail)',
    'Grid Size: 80 (High Detail)'
]

# Create 2x2 comparison figure
fig, axes = plt.subplots(2, 2, figsize=(12, 12))
axes = axes.flatten()

for idx, (grid_size, title) in enumerate(zip(grid_sizes, titles)):
    sampled_data.plot.hexbin(
        x='x',
        y='y',
        gridsize=grid_size,
        cmap='Greys',
        ax=axes[idx]
    )
    axes[idx].set_aspect('equal')
    axes[idx].axis('off')
    axes[idx].set_title(title, fontsize=14, fontweight='bold', pad=10)

plt.tight_layout()
plt.savefig('hexbin_comparison.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Grid size comparison complete!")
print("Output saved as: hexbin_comparison.png")
