import torch
import torch.nn.functional as F

def gram_matrix(features: torch.Tensor) -> torch.Tensor:
    """
    Compute the Gram matrix of a feature map.

    TODO:
    1. Get batch, channels, h, w from features.shape
    2. Reshape features to (batch*channels, h*w)
    3. Compute Gram: F @ F.T
    4. Normalise by (batch*channels*h*w)
    """
    pass

def style_loss(target_features: dict, style_grams: dict, layers: set) -> torch.Tensor:
    """
    Sum MSE between target's Gram matrices and reference style Gram matrices
    across all style layers.

    TODO:
    1. For each layer in `layers`:
       a. Compute target's Gram matrix from target_features[layer]
       b. Compute MSE between that and style_grams[layer]
    2. Return the sum
    """
    pass

# Quick test
if __name__ == "__main__":
    features = torch.randn(1, 64, 32, 32)
    g = gram_matrix(features)
    assert g.shape == (64, 64), f"Expected (64, 64), got {g.shape}"
    print("gram_matrix test passed")

    fake_target = {"conv_1": torch.randn(1, 64, 16, 16),
                   "conv_2": torch.randn(1, 128, 8, 8)}
    fake_style  = {"conv_1": torch.randn(64, 64),
                   "conv_2": torch.randn(128, 128)}
    loss = style_loss(fake_target, fake_style, {"conv_1", "conv_2"})
    print(f"style_loss test value: {loss.item():.4f}")
