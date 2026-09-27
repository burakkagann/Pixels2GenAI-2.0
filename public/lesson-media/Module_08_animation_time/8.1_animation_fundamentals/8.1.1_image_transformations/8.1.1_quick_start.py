import numpy as np
from PIL import Image

a = np.array(Image.open('python_logo.png').convert('RGB'))

# Brightness — divide every value
Image.fromarray(a // 2).save('dim.png')

# Horizontal flip — reverse the column axis
Image.fromarray(a[:, ::-1]).save('flip.png')

# Drop the green channel
g = a.copy(); g[:, :, 1] = 0
Image.fromarray(g).save('purple.png')
