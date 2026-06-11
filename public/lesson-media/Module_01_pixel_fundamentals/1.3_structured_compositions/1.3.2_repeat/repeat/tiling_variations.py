import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Configuration for three variations
variations = [
    {
        'title': 'Dense Grid (6x6)',
        'n_tiles': 6,
        'tile_width': 80,
        'spacing': 10,
        'color_func': lambda x, y: (min(255, 35 * y + 50), min(255, 35 * x + 50), 0)  # Capped at 255
    },
    {
        'title': 'Seamless Tiles',
        'n_tiles': 4,
        'tile_width': 125,
        'spacing': 0,  # No spacing - tiles touch each other
        'color_func': lambda x, y: (50 * y + 50, 50 * x + 50, 0)
    },
    {
        'title': 'Blue Diagonal Gradient',
        'n_tiles': 4,
        'tile_width': 125,
        'spacing': 15,
        'color_func': lambda x, y: (0, 0, min(255, 30 * (x + y) + 50))  # Blue gradient (capped at 255)
    }
]

# Create figure with 3 subplots
fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=150)
fig.suptitle('Tiling Pattern Variations', fontsize=16, fontweight='bold')

# Generate each variation
for idx, var in enumerate(variations):
    N_TILES = var['n_tiles']
    TILE_WIDTH = var['tile_width']
    SPACING = var['spacing']
    SIZE = TILE_WIDTH * N_TILES + SPACING
    color_func = var['color_func']

    # Create canvas
    canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

    # Generate tiles
    for y in range(N_TILES):
        for x in range(N_TILES):
            color = color_func(x, y)

            # Calculate position
            row_start = SPACING + y * TILE_WIDTH
            row_stop = (y + 1) * TILE_WIDTH
            col_start = SPACING + x * TILE_WIDTH
            col_stop = (x + 1) * TILE_WIDTH

            # Place tile
            canvas[row_start:row_stop, col_start:col_stop] = color

    # Display in subplot
    axes[idx].imshow(canvas)
    axes[idx].set_title(var['title'], fontsize=12, fontweight='bold')
    axes[idx].axis('off')

    # Add parameter annotations
    param_text = f"N_TILES={N_TILES}\nTILE_WIDTH={TILE_WIDTH}\nSPACING={SPACING}"
    axes[idx].text(
        0.5, -0.05,
        param_text,
        transform=axes[idx].transAxes,
        ha='center',
        va='top',
        fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
        family='monospace'
    )

plt.tight_layout()
plt.savefig('tiling_variations.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
