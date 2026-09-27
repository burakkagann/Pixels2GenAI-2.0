import numpy as np
from PIL import Image

a = np.array(Image.open('a.png'))    # shape (133, 300, 3)
b = np.array(Image.open('b.png'))    # shape (133, 300, 3)

print('A:', a.shape, 'B:', b.shape)

row = np.hstack([a, b])               # heights match → widths add
print('Row:', row.shape)              # (133, 600, 3)

Image.fromarray(row).save('quick_start_output.png')
