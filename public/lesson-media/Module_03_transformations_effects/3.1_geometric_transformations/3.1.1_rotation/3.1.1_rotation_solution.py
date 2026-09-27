import numpy as np
from scipy import ndimage
from PIL import Image

canvas_size = 400
rotation_angle = 30
background_color = [30, 30, 50]
shape_color      = [255, 150, 50]

canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
canvas[:, :] = background_color

shape_layer = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
shape_layer[150:250, 180:350] = shape_color

rotated_shape = ndimage.rotate(
    shape_layer, rotation_angle,
    reshape=False, mode='constant', cval=0,
)

mask = np.any(rotated_shape > 0, axis=2)
canvas[mask] = rotated_shape[mask]

Image.fromarray(canvas).save('my_rotation.png')
