import numpy as np
from PIL import Image

# Load all puzzle pieces
piece_a = np.array(Image.open('a.png'))
piece_b = np.array(Image.open('b.png'))
piece_c = np.array(Image.open('c.png'))
piece_d = np.array(Image.open('d.png'))
piece_e = np.array(Image.open('e.png'))
piece_f = np.array(Image.open('f.png'))

# Print all shapes to plan your approach
print("=== Puzzle Piece Shapes ===")
print(f"A: {piece_a.shape}")
print(f"B: {piece_b.shape}")
print(f"C: {piece_c.shape}")
print(f"D: {piece_d.shape}")
print(f"E: {piece_e.shape}")
print(f"F: {piece_f.shape}")

# === GOAL 1: Create horizontal row from D and E ===
# Hint: D and E have the same height (133 pixels)
# TODO: Combine D and E horizontally
row_de = np.hstack([piece_d, piece_e])
print(f"\nGoal 1 - Row D+E: {row_de.shape}")
Image.fromarray(row_de).save('exercise2_row_de.png')

# === GOAL 2: Create vertical column from A and C ===
# Hint: A and C have the same width (300 pixels)
# TODO: Combine A and C vertically
column_ac = np.vstack([piece_a, piece_c])
print(f"Goal 2 - Column A+C: {column_ac.shape}")
Image.fromarray(column_ac).save('exercise2_column_ac.png')

# === GOAL 3: Create a 2x2 grid ===
# Challenge: Combine A, B (top row) and C, D+E (bottom row)
# Hint: First build each row, then stack the rows

# Step 1: Build top row (A + B)
top_row = np.hstack([piece_a, piece_b])
print(f"\nGoal 3 - Building 2x2 grid:")
print(f"  Top row (A+B): {top_row.shape}")

# Step 2: Build bottom row (C + D + E)
# Note: C width is 300, D+E combined width is also 300
bottom_row = np.hstack([piece_c, piece_d, piece_e])
print(f"  Bottom row (C+D+E): {bottom_row.shape}")

# Step 3: Stack the rows vertically
grid = np.vstack([top_row, bottom_row])
print(f"  Final grid: {grid.shape}")
Image.fromarray(grid).save('exercise2_grid.png')

print("\n=== Challenge Extension ===")
print("Can you assemble the COMPLETE original image using all 6 pieces?")
print("Hint: Look at the source_image.png to see the target layout!")
