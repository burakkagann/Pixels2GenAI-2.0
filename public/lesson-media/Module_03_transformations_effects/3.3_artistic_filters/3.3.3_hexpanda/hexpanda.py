import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Configuration: grid size controls the level of detail
# Smaller values = larger hexagons = more abstract
# Larger values = smaller hexagons = more detail
grid_size = 30

# Step 1: Load and convert image to grayscale
panda_image = Image.open('panda.png')
panda_grayscale = panda_image.convert('L')
pixel_array = np.array(panda_grayscale)

# Step 2: Invert colors (white background becomes 0, dark pixels become high values)
# This is needed because hexbin plots density - we want dark areas to have high counts
inverted_pixels = 255 - pixel_array

# Step 3: Convert 2D array to pandas DataFrame for data manipulation
pixel_dataframe = pd.DataFrame(inverted_pixels)

# Step 4: Unstack to get (column, row, value) format
# The unstack() operation converts the 2D grid into a single Series
# with a MultiIndex containing (column, row) coordinates
pixel_series = pixel_dataframe.unstack()

# Step 5: Filter out background pixels (value = 0 after inversion)
# Only keep pixels that were originally dark (now have positive values)
foreground_pixels = pixel_series[pixel_series > 0]

# Step 6: Reset index to get x, y coordinates as columns
pixel_data = foreground_pixels.reset_index()
pixel_data.columns = ['x', 'y', 'intensity']

# Step 7: Invert y-coordinate for correct orientation
# Image coordinates have y=0 at top, matplotlib has y=0 at bottom
pixel_data['y'] = -pixel_data['y']

# Step 8: Random sampling to create density variation
# Using 25% of pixels creates a more artistic, scattered effect
sample_fraction = 4  # Use 1/4 of the pixels
sampled_data = pixel_data.sample(len(pixel_data) // sample_fraction)

# Step 9: Create hexbin visualization
# The hexbin plot aggregates points into hexagonal bins and colors by count
figure, axes = plt.subplots(figsize=(8, 8))
sampled_data.plot.hexbin(
    x='x',
    y='y',
    gridsize=grid_size,
    cmap='Greys',
    ax=axes
)

# Step 10: Clean up the plot appearance
axes.set_aspect('equal')
axes.axis('off')
plt.tight_layout()

# Step 11: Save the result
plt.savefig('hexpanda.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

print("Hexpanda visualization complete!")
print(f"Original image size: {pixel_array.shape}")
print(f"Foreground pixels: {len(foreground_pixels):,}")
print(f"Sampled pixels: {len(sampled_data):,}")
print(f"Grid size: {grid_size}")
print("Output saved as: hexpanda.png")
