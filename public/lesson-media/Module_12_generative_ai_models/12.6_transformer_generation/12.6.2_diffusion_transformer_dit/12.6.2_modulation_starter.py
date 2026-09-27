import torch
import torch.nn as nn

EMBED_DIM = 256
TIME_EMBED_DIM = 256

class AdaLNModulation(nn.Module):
    """Predict six values from the conditioning vector:
    (shift, scale, gate) for the attention branch +
    (shift, scale, gate) for the MLP branch.
    """

    def __init__(self):
        super().__init__()
        # TODO: SiLU + Linear(TIME_EMBED_DIM, 6 * EMBED_DIM)
        pass

    def forward(self, c):
        # TODO: pass c through the MLP
        # TODO: chunk the (B, 6*EMBED_DIM) output into 6 tensors of (B, EMBED_DIM)
        # TODO: return the 6 tensors
        pass


# Quick test
if __name__ == "__main__":
    mod = AdaLNModulation()
    c = torch.randn(4, TIME_EMBED_DIM)
    out = mod(c)
    assert len(out) == 6, f"Expected 6 outputs, got {len(out)}"
    for t in out:
        assert t.shape == (4, EMBED_DIM)
    print("AdaLNModulation test passed")
