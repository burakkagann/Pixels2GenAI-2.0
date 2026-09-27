import numpy as np
from PIL import Image

CANVAS_SIZE = 512
canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)

def add_cluster(canvas, cx, cy, num_stars, spread):
    x = np.random.normal(cx, spread, size=num_stars)
    y = np.random.normal(cy, spread, size=num_stars)
    x = np.clip(x, 0, canvas.shape[1] - 1).astype(int)
    y = np.clip(y, 0, canvas.shape[0] - 1).astype(int)
    canvas[y, x] = 255

# Galactic core
add_cluster(canvas, cx=256, cy=256, num_stars=300, spread=80)

# Satellite clusters
add_cluster(canvas, cx=100, cy=120, num_stars=80,  spread=30)
add_cluster(canvas, cx=400, cy=380, num_stars=120, spread=45)
add_cluster(canvas, cx=380, cy=100, num_stars=60,  spread=20)

# Sparse background fill
add_cluster(canvas, cx=256, cy=256, num_stars=100, spread=200)

Image.fromarray(canvas, mode='L').save('multi_cluster.png')
