import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

H, W = 200, 200

# TODO 1: build a 2D gradient where intensity = row + col,
#         scaled to 0..255 (uint8). Use np.indices for the (row, col) grid.

# TODO 2: convert to the long DataFrame using the same unstack + reset_index pipeline.

# TODO 3: sample ~50% of the pixels and plot.hexbin with gridsize=25, cmap='viridis'.

plt.savefig('gradient_hexbin.png', bbox_inches='tight', dpi=120)
