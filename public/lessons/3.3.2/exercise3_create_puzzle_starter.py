import numpy as np
from PIL import Image

# Step 1: Load any image (use source_image.png as example, or your own!)
# TODO: Replace with your own image path if desired
image = np.array(Image.open('source_image.png'))
print(f"Original image shape: {image.shape}")

# Step 2: Calculate slice boundaries for a 2x2 grid
height, width = image.shape[0], image.shape[1]
mid_y = height // 2  # Vertical midpoint
mid_x = width // 2   # Horizontal midpoint

print(f"Image dimensions: {height} x {width}")
print(f"Mid points: y={mid_y}, x={mid_x}")

# Step 3: Slice into 4 pieces (2x2 grid)
# TODO: Fill in the slicing indices to create 4 pieces
# Hint: Use image[start_y:end_y, start_x:end_x] syntax

top_left = image[0:mid_y, 0:mid_x]           # TODO: top-left quadrant
top_right = image[0:mid_y, mid_x:width]      # TODO: top-right quadrant
bottom_left = image[mid_y:height, 0:mid_x]   # TODO: bottom-left quadrant
bottom_right = image[mid_y:height, mid_x:width]  # TODO: bottom-right quadrant

# Print piece shapes to verify
print(f"\nPiece shapes:")
print(f"  Top-left: {top_left.shape}")
print(f"  Top-right: {top_right.shape}")
print(f"  Bottom-left: {bottom_left.shape}")
print(f"  Bottom-right: {bottom_right.shape}")

# Step 4: Reassemble the puzzle
# TODO: First combine pieces into rows, then stack rows vertically

# Build top row (left + right)
top_row = np.hstack([top_left, top_right])

# Build bottom row (left + right)
bottom_row = np.hstack([bottom_left, bottom_right])

# Stack rows to create complete image
reassembled = np.vstack([top_row, bottom_row])

print(f"\nReassembled image shape: {reassembled.shape}")

# Step 5: Save results
Image.fromarray(top_left).save('my_piece_tl.png')
Image.fromarray(top_right).save('my_piece_tr.png')
Image.fromarray(bottom_left).save('my_piece_bl.png')
Image.fromarray(bottom_right).save('my_piece_br.png')
Image.fromarray(reassembled).save('exercise3_reassembled.png')

# Step 6: Verify the reassembly is correct
if np.array_equal(image, reassembled):
    print("\nSUCCESS! Reassembled image matches the original!")
else:
    print("\nOops! Something went wrong - images don't match.")

print("\n=== Challenge: Shuffle the pieces! ===")
print("Try reassembling with pieces in wrong order to see what happens.")
print("Can you create an abstract art piece by intentional misarrangement?")
