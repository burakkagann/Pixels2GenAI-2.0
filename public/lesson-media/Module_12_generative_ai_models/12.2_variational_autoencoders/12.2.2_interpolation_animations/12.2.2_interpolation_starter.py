import torch

def linear_interpolate(z1, z2, t):
    # TODO: return (1 - t) * z1 + t * z2
    pass

def slerp(z1, z2, t):
    # TODO:
    #   1. Normalise z1, z2
    #   2. omega = acos(clamp(z1_norm . z2_norm, -1, 1))
    #   3. If omega is tiny, fall back to linear
    #   4. Apply slerp formula: sin((1-t)*omega)/sin(omega) * z1 + sin(t*omega)/sin(omega) * z2
    pass

if __name__ == '__main__':
    z1 = torch.randn(64)
    z2 = torch.randn(64)
    assert torch.allclose(linear_interpolate(z1, z2, 0.0), z1)
    assert torch.allclose(linear_interpolate(z1, z2, 1.0), z2)
    assert slerp(z1, z2, 0.5).shape == z1.shape
    print("All tests passed!")
