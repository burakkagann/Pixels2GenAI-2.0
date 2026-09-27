import numpy as np
from scipy import ndimage
from PIL import Image

canvas_size = 400
rotation_angle = 30
background_color = [30, 30, 50]
shape_color      = [255, 150, 50]

# TODO 1: create the canvas and fill it with background_color.
canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# TODO 2: draw a rectangle on a separate black layer (shape_layer)
#         using shape_layer[top:bottom, left:right] = shape_color.
shape_layer = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)

# TODO 3: rotate the shape_layer with ndimage.rotate(..., reshape=False, mode='constant', cval=0).

# TODO 4: build a boolean mask of where the rotated layer has any colour,
#         then copy those pixels onto canvas — canvas[mask] = rotated[mask].

Image.fromarray(canvas).save('my_rotation.png')
