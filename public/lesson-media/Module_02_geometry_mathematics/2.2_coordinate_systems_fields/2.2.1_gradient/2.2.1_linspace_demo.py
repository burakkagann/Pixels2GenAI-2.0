import numpy as np

# 5 evenly-spaced values from 0 to 100
print(np.linspace(0, 100, 5))
# → [ 0.  25.  50.  75. 100.]

# Cast to image bytes
print(np.linspace(0, 255, 5, dtype=np.uint8))
# → [ 0  63 127 191 255]
