import numpy as np

# (1, 1) → π/4 (up-right)
print(np.arctan2(1, 1))     # 0.7854

# (-1, 1) → 3π/4 (up-left)
print(np.arctan2(1, -1))    # 2.3562

# (0, 0) → 0 (undefined direction; convention picks 0)
print(np.arctan2(0, 0))     # 0.0
