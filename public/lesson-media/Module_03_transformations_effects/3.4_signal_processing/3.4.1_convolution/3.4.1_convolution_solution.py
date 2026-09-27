import numpy as np
from PIL import Image

def convolve(image, kernel):
    H, W = image.shape
    K = kernel.shape[0]
    pad = K // 2
    padded = np.pad(image, pad, mode='edge')

    output = np.zeros((H, W), dtype=np.float64)
    for y in range(H):
        for x in range(W):
            output[y, x] = np.sum(padded[y:y + K, x:x + K] * kernel)
    return output

# Pascal-triangle Gaussian-style 5×5
g = np.array([1, 4, 6, 4, 1])
gauss = np.outer(g, g)
gauss = gauss / gauss.sum()

photo = np.array(Image.open('bbtor.jpg').convert('L'), dtype=np.float64)
blurred = convolve(photo, gauss)

Image.fromarray(np.clip(blurred, 0, 255).astype(np.uint8), 'L').save('gauss_blur.png')
