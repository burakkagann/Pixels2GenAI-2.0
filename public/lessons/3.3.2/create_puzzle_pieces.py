import numpy as np
from PIL import Image

# Step 1: Create a colorful gradient source image (400x600 pixels)
# This creates a rainbow-like gradient that makes pieces easy to identify
height, width = 400, 600
source_image = np.zeros((height, width, 3), dtype=np.uint8)

# Create horizontal color gradient (red to blue)
for x in range(width):
    red = int(255 * (1 - x / width))    # Red decreases left to right
    blue = int(255 * (x / width))        # Blue increases left to right
    source_image[:, x, 0] = red
    source_image[:, x, 2] = blue

# Add vertical green gradient for more visual interest
for y in range(height):
    green = int(200 * (1 - y / height))  # Green decreases top to bottom
    source_image[y, :, 1] = green

# Step 2: Save the complete source image
Image.fromarray(source_image).save('source_image.png')
print(f"Created source_image.png with shape {source_image.shape}")

# Step 3: Slice the image into 6 puzzle pieces
# Layout:
#   +-------+-------+
#   |   a   |   b   |
#   +-------+---+---+
#   |   c   | d | e |
#   +-------+---+---+
#   |       f       |
#   +---------------+

# Calculate slice boundaries
mid_x = width // 2           # 300
third_x = 2 * width // 3     # 400
row1_end = height // 3       # 133
row2_end = 2 * height // 3   # 266

# Create pieces with different sizes (to demonstrate shape matching)
piece_a = source_image[0:row1_end, 0:mid_x]           # Top-left
piece_b = source_image[0:row1_end, mid_x:width]       # Top-right
piece_c = source_image[row1_end:row2_end, 0:mid_x]    # Middle-left
piece_d = source_image[row1_end:row2_end, mid_x:third_x]   # Middle-center
piece_e = source_image[row1_end:row2_end, third_x:width]   # Middle-right
piece_f = source_image[row2_end:height, 0:width]      # Bottom (full width)

# Save all pieces
pieces = {'a': piece_a, 'b': piece_b, 'c': piece_c,
          'd': piece_d, 'e': piece_e, 'f': piece_f}

for name, piece in pieces.items():
    Image.fromarray(piece).save(f'{name}.png')
    print(f"Created {name}.png with shape {piece.shape}")

# Step 4: Create a visual showing all pieces with labels
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 3, figsize=(12, 8))
fig.suptitle('Puzzle Pieces - Can You Reassemble Them?', fontsize=16, fontweight='bold')

piece_list = [('a', piece_a), ('b', piece_b), ('c', piece_c),
              ('d', piece_d), ('e', piece_e), ('f', piece_f)]

for idx, (name, piece) in enumerate(piece_list):
    row, col = idx // 3, idx % 3
    axes[row, col].imshow(piece)
    axes[row, col].set_title(f'{name}.png\nShape: {piece.shape}', fontsize=12)
    axes[row, col].axis('off')

plt.tight_layout()
plt.savefig('puzzle_pieces_overview.png', dpi=150, bbox_inches='tight')
plt.close()

print("\nAll puzzle pieces created successfully!")
print("Students should use np.vstack and np.hstack to reassemble.")
