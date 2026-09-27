import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def create_checkerboard(size=200, tile_size=25):
    """Create a colorful checkerboard pattern."""
    image = np.zeros((size, size, 3), dtype=np.uint8)
    colors = [(255, 100, 100), (100, 100, 255), (100, 255, 100), (255, 255, 100)]
    for row in range(size // tile_size):
        for col in range(size // tile_size):
            color = colors[(row + col) % len(colors)]
            y_start, y_end = row * tile_size, (row + 1) * tile_size
            x_start, x_end = col * tile_size, (col + 1) * tile_size
            image[y_start:y_end, x_start:x_end] = color
    return image

def apply_wave_distortion(image, amplitude, frequency):
    """Apply horizontal wave distortion with given parameters."""
    size = image.shape[0]
    distorted = np.zeros_like(image)
    for y in range(size):
        for x in range(size):
            offset = int(amplitude * np.sin(2 * np.pi * frequency * y / size))
            source_x = (x + offset) % size
            distorted[y, x] = image[y, source_x]
    return distorted

# Create base checkerboard
base_image = create_checkerboard()

# Define parameter variations
variations = [
    (10, 2, "Low Amplitude\nLow Frequency"),
    (30, 2, "High Amplitude\nLow Frequency"),
    (10, 6, "Low Amplitude\nHigh Frequency"),
    (30, 6, "High Amplitude\nHigh Frequency"),
]

# Create 2x2 comparison grid
fig, axes = plt.subplots(2, 2, figsize=(8, 8), dpi=100)
axes = axes.flatten()

for i, (amp, freq, title) in enumerate(variations):
    distorted = apply_wave_distortion(base_image, amp, freq)
    axes[i].imshow(distorted)
    axes[i].set_title(title, fontsize=11, fontweight='bold')
    axes[i].axis('off')

plt.tight_layout()
plt.savefig('wave_variations_grid.png', dpi=100, bbox_inches='tight')
plt.close()

