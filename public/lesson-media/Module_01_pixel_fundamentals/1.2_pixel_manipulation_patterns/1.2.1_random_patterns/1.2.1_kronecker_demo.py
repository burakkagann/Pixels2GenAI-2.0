import numpy as np

# Original: 2x2 array
small = np.array([[1, 2], [3, 4]])

# Scaling matrix: each element becomes a 3x3 block
scale = np.ones((3, 3))

# Kronecker product result: 6x6 array
large = np.kron(small, scale)
# Result: each original value repeated in 3x3 blocks
print(large)
