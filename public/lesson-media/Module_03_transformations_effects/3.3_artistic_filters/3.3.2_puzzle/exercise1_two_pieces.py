import numpy as np
from PIL import Image

# Load two puzzle pieces with matching heights
piece_a = np.array(Image.open('a.png'))
piece_c = np.array(Image.open('c.png'))

# Print shapes to understand the arrays
print("=== Array Shapes ===")
print(f"Piece A: {piece_a.shape}")
print(f"Piece C: {piece_c.shape}")

# Stack vertically (pieces A and C have the same WIDTH)
vertical_result = np.vstack([piece_a, piece_c])
print(f"\nAfter vstack([A, C]): {vertical_result.shape}")
Image.fromarray(vertical_result).save('exercise1_vstack.png')

# Stack horizontally (pieces A and C have the same HEIGHT)
horizontal_result = np.hstack([piece_a, piece_c])
print(f"After hstack([A, C]): {horizontal_result.shape}")
Image.fromarray(horizontal_result).save('exercise1_hstack.png')

print("\n=== Reflection Questions ===")
print("1. What changed in the shape after vstack? Which dimension increased?")
print("2. What changed in the shape after hstack? Which dimension increased?")
print("3. Both operations worked - what do A and C have in common?")
print("\nSaved: exercise1_vstack.png and exercise1_hstack.png")
