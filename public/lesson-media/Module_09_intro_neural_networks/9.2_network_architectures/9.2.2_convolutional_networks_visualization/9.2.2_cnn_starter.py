import numpy as np

def conv2d(x, W, b, stride=1):
    """Multi-filter 2D convolution with bias.
    x: (H, W, C_in), W: (K, k, k, C_in), b: (K,)
    Returns: (H_out, W_out, K)
    """
    H, W_in, C = x.shape
    K, kh, kw, _ = W.shape
    # TODO: implement using nested loops or im2col.

def maxpool2d(x, size=2, stride=2):
    """2x2 max pool with stride 2."""
    # TODO

def relu(x):
    return np.maximum(0, x)

# Build the network
def forward(image):
    x = image[..., None]                # (28, 28, 1)
    x = relu(conv2d(x, W1, b1))         # (28, 28, 4)
    x = maxpool2d(x)                    # (14, 14, 4)
    x = relu(conv2d(x, W2, b2))         # (14, 14, 8)
    x = maxpool2d(x)                    # (7, 7, 8)
    x = x.flatten()
    return W3 @ x + b3                  # logits
