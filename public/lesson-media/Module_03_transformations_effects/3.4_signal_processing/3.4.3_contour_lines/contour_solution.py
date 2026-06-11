import numpy as np
from PIL import Image

# Set random seed for reproducibility (change for different results)
np.random.seed(42)

# Step 1: Create coordinate grid
size = 400
dim = np.linspace(-10, 10, size)
x, y, _ = np.meshgrid(dim, dim, [1])

# Step 2: Generate random hills (between 3 and 5)
num_hills = 4  # You could also use: np.random.randint(3, 6)

# Random positions within the grid (avoid edges)
position_x = np.random.uniform(-8, 8, num_hills)
position_y = np.random.uniform(-8, 8, num_hills)

# Random widths (2.0 to 6.0 creates nice visible hills)
width_x = np.random.uniform(2.0, 6.0, num_hills)
width_y = np.random.uniform(2.0, 6.0, num_hills)

print(f"Generated {num_hills} hills:")
for i in range(num_hills):
    print(f"  Hill {i+1}: position=({position_x[i]:.1f}, {position_y[i]:.1f}), "
          f"width=({width_x[i]:.1f}, {width_y[i]:.1f})")

# Step 3: Calculate height using Gaussian formula
# Each hill contributes to the total height
d = np.sqrt(((x - position_x) / width_x) ** 2 + ((y - position_y) / width_y) ** 2)
z = np.exp(-d ** 2)
z = z.sum(axis=2)  # Combine all hills

# Normalize to 0-1 range
znorm = (z - z.min()) / (z.max() - z.min())

# Step 4: Create stepped contour visualization
n_levels = 10  # More levels for finer detail
step_size = 255 // n_levels
contour = (znorm * n_levels).astype(np.uint8) * step_size

# Save stepped contour
image = Image.fromarray(contour, mode='L')
image.save('random_terrain.png')
print(f"\nSaved random_terrain.png with {n_levels} contour levels")

# Bonus: Also create isoline version
isolines = ((znorm * 100).round() % 12) == 0
isolines = (isolines * 255).astype(np.uint8)
image = Image.fromarray(isolines, mode='L')
image.save('random_terrain_isolines.png')
print("Saved random_terrain_isolines.png (isoline version)")

print("\nDone! Your random terrain has been generated.")
