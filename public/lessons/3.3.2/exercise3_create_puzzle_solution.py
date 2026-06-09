import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# === PART 1: Create puzzle from source image ===
print("=== Creating Puzzle from Source Image ===\n")

# Load the source image
image = np.array(Image.open('source_image.png'))
height, width = image.shape[0], image.shape[1]
print(f"Original image: {height} x {width} pixels")

# Calculate slice boundaries for a 2x2 grid
mid_y = height // 2
mid_x = width // 2

# Slice into 4 pieces
top_left = image[0:mid_y, 0:mid_x]
top_right = image[0:mid_y, mid_x:width]
bottom_left = image[mid_y:height, 0:mid_x]
bottom_right = image[mid_y:height, mid_x:width]

# Print shapes for verification
print(f"\nPuzzle pieces created:")
print(f"  Top-left:     {top_left.shape}")
print(f"  Top-right:    {top_right.shape}")
print(f"  Bottom-left:  {bottom_left.shape}")
print(f"  Bottom-right: {bottom_right.shape}")

# === PART 2: Correct reassembly ===
print("\n=== Reassembling Correctly ===")

# Step 1: Build rows using hstack (horizontal stacking)
# hstack requires arrays with the SAME HEIGHT
top_row = np.hstack([top_left, top_right])
bottom_row = np.hstack([bottom_left, bottom_right])

print(f"Top row after hstack: {top_row.shape}")
print(f"Bottom row after hstack: {bottom_row.shape}")

# Step 2: Stack rows using vstack (vertical stacking)
# vstack requires arrays with the SAME WIDTH
correct_assembly = np.vstack([top_row, bottom_row])
print(f"Final assembly: {correct_assembly.shape}")

# Verify correctness
if np.array_equal(image, correct_assembly):
    print("Verification: PERFECT MATCH!")
else:
    print("Verification: Something went wrong!")

Image.fromarray(correct_assembly).save('exercise3_correct.png')

# === PART 3: Shuffled assembly (artistic variation) ===
print("\n=== Creating Artistic Shuffled Version ===")

# Shuffle pieces to create abstract art
# Let's swap diagonals
shuffled_top = np.hstack([bottom_right, top_left])
shuffled_bottom = np.hstack([top_right, bottom_left])
shuffled_assembly = np.vstack([shuffled_top, shuffled_bottom])

Image.fromarray(shuffled_assembly).save('exercise3_shuffled.png')
print("Created shuffled version - notice how colors are now mixed!")

# === PART 4: Create a visual comparison ===
print("\n=== Creating Comparison Figure ===")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(image)
axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
axes[0].axis('off')

axes[1].imshow(correct_assembly)
axes[1].set_title('Correctly Reassembled', fontsize=12, fontweight='bold')
axes[1].axis('off')

axes[2].imshow(shuffled_assembly)
axes[2].set_title('Shuffled (Abstract Art)', fontsize=12, fontweight='bold')
axes[2].axis('off')

plt.tight_layout()
plt.savefig('exercise3_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n=== Summary ===")
print("Key insights:")
print("1. Slicing uses [y_start:y_end, x_start:x_end] (rows first, columns second)")
print("2. hstack combines arrays LEFT-to-RIGHT (widths add up)")
print("3. vstack combines arrays TOP-to-BOTTOM (heights add up)")
print("4. Dimension compatibility is crucial for successful concatenation")
print("\nSaved: exercise3_correct.png, exercise3_shuffled.png, exercise3_comparison.png")
