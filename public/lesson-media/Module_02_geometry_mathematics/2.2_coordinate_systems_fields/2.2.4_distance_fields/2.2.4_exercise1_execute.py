import numpy as np
from PIL import Image

SIZE = 512
CENTER_X, CENTER_Y = 256, 256

Y, X = np.ogrid[0:SIZE, 0:SIZE]
distance_field = np.sqrt((X - CENTER_X) ** 2 + (Y - CENTER_Y) ** 2)

normalized = (distance_field / distance_field.max() * 255).astype(np.uint8)
Image.fromarray(normalized, mode='L').save('simple_distance_field.png')

print(f"Min distance: {distance_field.min():.1f}")
print(f"Max distance: {distance_field.max():.1f}")
