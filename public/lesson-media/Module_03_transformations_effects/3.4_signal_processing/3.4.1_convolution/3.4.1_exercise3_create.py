import numpy as np
from PIL import Image

def convolve(image, kernel):
    """Same-size 2D convolution with edge-replicate padding."""
    H, W = image.shape
    K = kernel.shape[0]              # assume square kernel
    pad = K // 2

    # TODO 1: pad the image with mode='edge'.
    # TODO 2: allocate the output array.
    # TODO 3: nested loop over (y, x); accumulate the weighted sum.
    return output

# A 5×5 Gaussian-like kernel (Pascal's triangle outer product)
g = np.array([1, 4, 6, 4, 1])
gauss = np.outer(g, g) / np.sum(np.outer(g, g))

photo = np.array(Image.open('bbtor.jpg').convert('L'), dtype=np.float64)
blurred = convolve(photo, gauss)

Image.fromarray(np.clip(blurred, 0, 255).astype(np.uint8), 'L').save('gauss_blur.png')
