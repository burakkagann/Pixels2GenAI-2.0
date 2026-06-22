"""DiT (Diffusion Transformer) block: minimal implementation.

Demonstrates the central architectural innovation of DiT: adaptive layer norm
(adaLN) conditioned on the diffusion timestep. The model replaces the U-Net in
a diffusion pipeline with a transformer that operates on flattened image patches.

This script defines and forward-runs a single DiT block on synthetic data; it
does NOT train a full diffusion model. For a full pipeline see the Hugging Face
diffusers PixArt implementation, which uses the same architectural ideas.

Author: Pixels2GenAI Project
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


PATCH_SIZE = 4         # image patches: 4x4 pixels each
IMAGE_SIZE = 32        # 32 / 4 = 8 patches per side, so 64 patches total
EMBED_DIM = 256
NUM_HEADS = 4
NUM_LAYERS = 4
HIDDEN_FACTOR = 4
TIME_EMBED_DIM = 256


def sinusoidal_time_embedding(t: torch.Tensor, dim: int) -> torch.Tensor:
    """Standard transformer-style sinusoidal embedding for the diffusion timestep."""
    half = dim // 2
    freqs = torch.exp(-math.log(10_000) * torch.arange(half, device=t.device) / half)
    args = t[:, None].float() * freqs[None]
    return torch.cat([torch.cos(args), torch.sin(args)], dim=-1)


class PatchEmbedding(nn.Module):
    """Slice the image into PATCH_SIZE x PATCH_SIZE patches and project each one to EMBED_DIM."""

    def __init__(self, in_channels: int = 3):
        super().__init__()
        self.proj = nn.Conv2d(in_channels, EMBED_DIM,
                              kernel_size=PATCH_SIZE, stride=PATCH_SIZE)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.proj(x)                  # (B, EMBED_DIM, H/P, W/P)
        return x.flatten(2).transpose(1, 2)   # (B, num_patches, EMBED_DIM)


class AdaLNModulation(nn.Module):
    """Predict the gain, bias, and gate values from the conditioning vector."""

    def __init__(self):
        super().__init__()
        # 6 outputs per block: scale1, shift1, gate1 (attention), scale2, shift2, gate2 (MLP)
        self.mlp = nn.Sequential(
            nn.SiLU(),
            nn.Linear(TIME_EMBED_DIM, 6 * EMBED_DIM),
        )

    def forward(self, c: torch.Tensor) -> tuple[torch.Tensor, ...]:
        params = self.mlp(c)              # (B, 6 * EMBED_DIM)
        return params.chunk(6, dim=-1)    # 6 tensors of (B, EMBED_DIM) each


class DiTBlock(nn.Module):
    """Transformer block with adaptive LayerNorm conditioned on diffusion timestep."""

    def __init__(self):
        super().__init__()
        self.norm1 = nn.LayerNorm(EMBED_DIM, elementwise_affine=False, eps=1e-6)
        self.attn = nn.MultiheadAttention(EMBED_DIM, NUM_HEADS, batch_first=True)
        self.norm2 = nn.LayerNorm(EMBED_DIM, elementwise_affine=False, eps=1e-6)
        self.mlp = nn.Sequential(
            nn.Linear(EMBED_DIM, HIDDEN_FACTOR * EMBED_DIM),
            nn.GELU(),
            nn.Linear(HIDDEN_FACTOR * EMBED_DIM, EMBED_DIM),
        )
        self.modulation = AdaLNModulation()

    def forward(self, x: torch.Tensor, c: torch.Tensor) -> torch.Tensor:
        shift1, scale1, gate1, shift2, scale2, gate2 = self.modulation(c)

        # Self-attention path
        h = self.norm1(x)
        h = h * (1 + scale1.unsqueeze(1)) + shift1.unsqueeze(1)
        attn_out, _ = self.attn(h, h, h, need_weights=False)
        x = x + gate1.unsqueeze(1) * attn_out

        # MLP path
        h = self.norm2(x)
        h = h * (1 + scale2.unsqueeze(1)) + shift2.unsqueeze(1)
        x = x + gate2.unsqueeze(1) * self.mlp(h)
        return x


class TinyDiT(nn.Module):
    def __init__(self):
        super().__init__()
        self.patchify = PatchEmbedding(in_channels=3)
        num_patches = (IMAGE_SIZE // PATCH_SIZE) ** 2
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches, EMBED_DIM))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

        self.time_proj = nn.Sequential(
            nn.Linear(TIME_EMBED_DIM, TIME_EMBED_DIM),
            nn.SiLU(),
            nn.Linear(TIME_EMBED_DIM, TIME_EMBED_DIM),
        )

        self.blocks = nn.ModuleList([DiTBlock() for _ in range(NUM_LAYERS)])
        self.norm_out = nn.LayerNorm(EMBED_DIM, elementwise_affine=False, eps=1e-6)
        # Output: predict noise as patches; reshape back to image later
        self.head = nn.Linear(EMBED_DIM, PATCH_SIZE * PATCH_SIZE * 3)

    def forward(self, x: torch.Tensor, t: torch.Tensor) -> torch.Tensor:
        b = x.size(0)
        c = self.time_proj(sinusoidal_time_embedding(t, TIME_EMBED_DIM))

        h = self.patchify(x) + self.pos_embed
        for block in self.blocks:
            h = block(h, c)
        h = self.norm_out(h)
        h = self.head(h)
        return h.reshape(b, IMAGE_SIZE // PATCH_SIZE, IMAGE_SIZE // PATCH_SIZE,
                         3, PATCH_SIZE, PATCH_SIZE).permute(0, 3, 1, 4, 2, 5).reshape(
            b, 3, IMAGE_SIZE, IMAGE_SIZE)


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    model = TinyDiT().to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"TinyDiT parameter count: {n_params:,}")

    # Synthetic input: a batch of "noisy images" + a batch of timesteps
    x = torch.randn(4, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
    t = torch.randint(0, 1000, (4,), device=device)

    with torch.no_grad():
        noise_pred = model(x, t)

    print(f"Input shape:  {tuple(x.shape)}")
    print(f"Timestep:     {tuple(t.shape)} (values {t.tolist()})")
    print(f"Output shape: {tuple(noise_pred.shape)} (predicted noise per pixel)")
    print("\nIn a real diffusion training loop, the model would minimise MSE")
    print("between this noise prediction and the noise actually added to the input.")


if __name__ == "__main__":
    main()
