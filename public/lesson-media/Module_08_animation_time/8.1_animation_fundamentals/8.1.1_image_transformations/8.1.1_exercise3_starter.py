import numpy as np
from PIL import Image

def vignette(image, strength=1.0):
    """Return a new image with brightness fading from full at the centre
    to (1 - strength) at the corners."""
    H, W, _ = image.shape

    # TODO 1: build the squared-distance field with np.mgrid

    # TODO 2: normalise so the centre is 0 and the corners are 1

    # TODO 3: brightness factor = 1 - strength * normalised_distance
    #         (clip to [0, 1] to be safe)

    # TODO 4: multiply each channel by the brightness factor, return a uint8 image
    return image

a = np.array(Image.open('python_logo.png').convert('RGB'))
Image.fromarray(vignette(a, strength=0.85)).save('vignette.png')
