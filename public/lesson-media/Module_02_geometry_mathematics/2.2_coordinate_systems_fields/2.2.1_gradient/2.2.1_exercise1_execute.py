import numpy as np
from PIL import Image

height = 300
width = 800
gradient_values = np.linspace(0, 255, width, dtype=np.uint8)
gradient_image = np.tile(gradient_values, (height, 1))

Image.fromarray(gradient_image, mode='L').save('simple_gradient.png')

print(f"First 5 values: {gradient_values[:5]}")
print(f"Last 5 values:  {gradient_values[-5:]}")
print(f"Middle value:   {gradient_values[width // 2]}")
