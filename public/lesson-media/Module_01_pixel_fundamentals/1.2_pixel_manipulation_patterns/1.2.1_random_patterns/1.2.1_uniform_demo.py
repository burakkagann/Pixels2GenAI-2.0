import numpy as np

# Every RGB value has equal 1/256 probability
random_rgb = np.random.randint(0, 256, size=(5, 5, 3), dtype=np.uint8)

# This gives us 256^3 = 16,777,216 possible colors per pixel
total_colors = 256 ** 3
print(f"Total possible colors: {total_colors:,}")
