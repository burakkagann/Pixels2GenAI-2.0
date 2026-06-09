
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
    # TODO: Generate Gaussian-distributed x coordinates around center_x
    # Hint: Use np.random.normal(mean, std_dev, size)
    x_coords = None  # Replace with your code

    # TODO: Generate Gaussian-distributed y coordinates around center_y
    y_coords = None  # Replace with your code

    # TODO: Clip coordinates to stay within canvas bounds
    # Hint: Use np.clip(array, min, max).astype(int)
    x_coords = None  # Replace with your code
    y_coords = None  # Replace with your code

    # TODO: Place stars on canvas using integer array indexing
    # Hint: canvas[y_coords, x_coords] = brightness_value
    pass  # Replace with your code

# TODO: Add at least 3 clusters with different parameters
# Example cluster definitions (customize these):
# Cluster 1: Large central cluster
# add_cluster(canvas, center_x=?, center_y=?, num_stars=?, spread=?)

# Cluster 2: Smaller cluster to the upper-left
# add_cluster(canvas, ...)

# Cluster 3: Another small cluster
# add_cluster(canvas, ...)

# Save the result
image = Image.fromarray(canvas, mode='L')
image.save('multi_cluster.png')
