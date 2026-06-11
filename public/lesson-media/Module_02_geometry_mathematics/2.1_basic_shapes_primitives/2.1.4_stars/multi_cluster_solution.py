

import numpy as np
from PIL import Image

# Configuration
CANVAS_SIZE = 512
BACKGROUND = 0

# Create a black canvas
canvas = np.full((CANVAS_SIZE, CANVAS_SIZE), BACKGROUND, dtype=np.uint8)

def add_cluster(canvas, center_x, center_y, num_stars, spread):
    """
    Add a star cluster to the canvas using Gaussian distribution.

    Parameters:
        canvas: The image array to modify
        center_x: X coordinate of cluster center
        center_y: Y coordinate of cluster center
        num_stars: Number of stars in this cluster
        spread: Standard deviation (controls cluster tightness)
    """
    # Generate Gaussian-distributed coordinates
    x_coords = np.random.normal(center_x, spread, size=num_stars)
    y_coords = np.random.normal(center_y, spread, size=num_stars)

    # Clip to canvas bounds and convert to integers
    x_coords = np.clip(x_coords, 0, canvas.shape[1] - 1).astype(int)
    y_coords = np.clip(y_coords, 0, canvas.shape[0] - 1).astype(int)

    # Place stars using integer array indexing
    canvas[y_coords, x_coords] = 255

# Cluster 1: Large central cluster (main galaxy core)
add_cluster(canvas, center_x=256, center_y=256, num_stars=300, spread=80)

# Cluster 2: Smaller cluster to the upper-left (satellite cluster)
add_cluster(canvas, center_x=100, center_y=120, num_stars=80, spread=30)

# Cluster 3: Medium cluster to the lower-right
add_cluster(canvas, center_x=400, center_y=380, num_stars=120, spread=45)

# Cluster 4: Small tight cluster (globular cluster style)
add_cluster(canvas, center_x=380, center_y=100, num_stars=60, spread=20)

# Cluster 5: Sparse background stars (very spread out)
add_cluster(canvas, center_x=256, center_y=256, num_stars=100, spread=200)

# Save the result
image = Image.fromarray(canvas, mode='L')
image.save('multi_cluster.png')
