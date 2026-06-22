import math
import torch
import torch.nn as nn
import torch.nn.functional as F

# =============================================================================
# Building Blocks
# =============================================================================

class SinusoidalPositionEmbeddings(nn.Module):
    """
    Sinusoidal embeddings for encoding the timestep t.

    These embeddings allow the network to distinguish between different
    points along the flow trajectory (t=0 is noise, t=1 is data).

    This is the same technique used in Transformers and DDPM.
    """

    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, time):
        device = time.device
        half_dim = self.dim // 2
        embeddings = math.log(10000) / (half_dim - 1)
        embeddings = torch.exp(torch.arange(half_dim, device=device) * -embeddings)
        embeddings = time[:, None] * embeddings[None, :]
        embeddings = torch.cat((embeddings.sin(), embeddings.cos()), dim=-1)
        return embeddings

class ResidualBlock(nn.Module):
    """
    Residual block with timestep conditioning.

    Each block consists of:
    1. GroupNorm + activation + convolution
    2. Timestep embedding injection
    3. GroupNorm + activation + convolution
    4. Residual connection

    GroupNorm is preferred over BatchNorm for generative models
    as it works better with small batch sizes.
    """

    def __init__(self, in_channels, out_channels, time_emb_dim, groups=8):
        super().__init__()

        self.time_mlp = nn.Sequential(
            nn.SiLU(),
            nn.Linear(time_emb_dim, out_channels)
        )

        self.block1 = nn.Sequential(
            nn.GroupNorm(groups, in_channels),
            nn.SiLU(),
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        )

        self.block2 = nn.Sequential(
            nn.GroupNorm(groups, out_channels),
            nn.SiLU(),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1)
        )

        # Residual connection (1x1 conv if channels change)
        if in_channels != out_channels:
            self.residual_conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        else:
            self.residual_conv = nn.Identity()

    def forward(self, x, time_emb):
        # First convolution block
        h = self.block1(x)

        # Add timestep embedding (broadcast across spatial dimensions)
        time_emb = self.time_mlp(time_emb)
        h = h + time_emb[:, :, None, None]

        # Second convolution block
        h = self.block2(h)

        # Residual connection
        return h + self.residual_conv(x)

class AttentionBlock(nn.Module):
    """
    Self-attention block for capturing global context.

    Attention allows the network to consider relationships between
    distant pixels, which is important for generating coherent patterns.

    Used at lower resolutions (e.g., 8x8, 16x16) where it's computationally
    feasible. At higher resolutions, it would be too expensive.
    """

    def __init__(self, channels, num_heads=4):
        super().__init__()
        self.channels = channels
        self.num_heads = num_heads
        self.head_dim = channels // num_heads

        self.norm = nn.GroupNorm(8, channels)
        self.qkv = nn.Conv2d(channels, channels * 3, kernel_size=1)
        self.proj = nn.Conv2d(channels, channels, kernel_size=1)

    def forward(self, x):
        b, c, h, w = x.shape
        residual = x

        x = self.norm(x)

        # Compute query, key, value
        qkv = self.qkv(x)
        qkv = qkv.reshape(b, 3, self.num_heads, self.head_dim, h * w)
        q, k, v = qkv[:, 0], qkv[:, 1], qkv[:, 2]

        # Scaled dot-product attention
        scale = self.head_dim ** -0.5
        attn = torch.einsum('bnci,bncj->bnij', q, k) * scale
        attn = F.softmax(attn, dim=-1)

        # Apply attention to values
        out = torch.einsum('bnij,bncj->bnci', attn, v)
        out = out.reshape(b, c, h, w)

        # Project and add residual
        out = self.proj(out)
        return out + residual

class Downsample(nn.Module):
    """Downsample spatial dimensions by 2x using strided convolution."""

    def __init__(self, channels):
        super().__init__()
        self.conv = nn.Conv2d(channels, channels, kernel_size=3, stride=2, padding=1)

    def forward(self, x):
        return self.conv(x)

class Upsample(nn.Module):
    """Upsample spatial dimensions by 2x using nearest neighbor + convolution."""

    def __init__(self, channels):
        super().__init__()
        self.conv = nn.Conv2d(channels, channels, kernel_size=3, padding=1)

    def forward(self, x):
        x = F.interpolate(x, scale_factor=2, mode='nearest')
        return self.conv(x)

# =============================================================================
# Main U-Net Model
# =============================================================================

class FlowMatchingUNet(nn.Module):
    """
    U-Net for Flow Matching velocity prediction.

    Architecture:
    - Encoder: progressively downsample while increasing channels
    - Bottleneck: lowest resolution processing with attention
    - Decoder: progressively upsample with skip connections

    The network predicts v(x_t, t): the velocity at position x_t and time t
    that points toward the data distribution.

    This is nearly identical to the DDPM U-Net, demonstrating that
    the same architecture can be used for both approaches.

    Parameters:
        in_channels: Number of input channels (3 for RGB)
        base_channels: Base channel count (multiplied at each level)
        channel_mults: Channel multipliers for each level
        num_res_blocks: Residual blocks per level
        attention_resolutions: Resolutions at which to apply attention
        time_emb_dim: Dimension of timestep embeddings
    """

    def __init__(
        self,
        in_channels=3,
        base_channels=64,
        channel_mults=(1, 2, 4, 8),
        num_res_blocks=2,
        attention_resolutions=(8, 16),
        time_emb_dim=256
    ):
        super().__init__()

        self.in_channels = in_channels
        self.base_channels = base_channels

        # Timestep embedding network
        self.time_embedding = nn.Sequential(
            SinusoidalPositionEmbeddings(base_channels),
            nn.Linear(base_channels, time_emb_dim),
            nn.SiLU(),
            nn.Linear(time_emb_dim, time_emb_dim)
        )

        # Initial convolution
        self.init_conv = nn.Conv2d(in_channels, base_channels, kernel_size=3, padding=1)

        # Build encoder
        self.encoder = nn.ModuleList()
        self.downsample = nn.ModuleList()

        channels = [base_channels]
        in_ch = base_channels
        current_resolution = 64  # Assuming 64x64 input

        for level, mult in enumerate(channel_mults):
            out_ch = base_channels * mult

            # Residual blocks at this level
            for _ in range(num_res_blocks):
                block = ResidualBlock(in_ch, out_ch, time_emb_dim)
                self.encoder.append(block)
                in_ch = out_ch
                channels.append(in_ch)

            # Attention at specified resolutions
            if current_resolution in attention_resolutions:
                self.encoder.append(AttentionBlock(in_ch))
                channels.append(in_ch)

            # Downsample (except at last level)
            if level < len(channel_mults) - 1:
                self.downsample.append(Downsample(in_ch))
                channels.append(in_ch)
                current_resolution //= 2

        # Bottleneck
        self.bottleneck = nn.ModuleList([
            ResidualBlock(in_ch, in_ch, time_emb_dim),
            AttentionBlock(in_ch),
            ResidualBlock(in_ch, in_ch, time_emb_dim)
        ])

        # Build decoder
        self.decoder = nn.ModuleList()
        self.upsample = nn.ModuleList()

        for level, mult in reversed(list(enumerate(channel_mults))):
            out_ch = base_channels * mult

            # Residual blocks with skip connections
            for i in range(num_res_blocks + 1):
                skip_ch = channels.pop()
                block = ResidualBlock(in_ch + skip_ch, out_ch, time_emb_dim)
                self.decoder.append(block)
                in_ch = out_ch

            # Attention at specified resolutions
            if current_resolution in attention_resolutions:
                self.decoder.append(AttentionBlock(in_ch))

            # Upsample (except at first level)
            if level > 0:
                self.upsample.append(Upsample(in_ch))
                current_resolution *= 2

        # Final layers
        self.final = nn.Sequential(
            nn.GroupNorm(8, base_channels),
            nn.SiLU(),
            nn.Conv2d(base_channels, in_channels, kernel_size=3, padding=1)
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights with small values for stable training."""
        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
                if module.bias is not None:
                    nn.init.zeros_(module.bias)
            elif isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, x, t):
        """
        Forward pass predicting velocity v(x_t, t).

        Parameters:
            x: Input tensor [B, C, H, W] at time t along the flow
            t: Timestep tensor [B] in range [0, 1]

        Returns:
            Predicted velocity [B, C, H, W] pointing toward data
        """
        # Compute timestep embedding
        time_emb = self.time_embedding(t)

        # Initial convolution
        x = self.init_conv(x)

        # Encoder with skip connections
        skips = [x]
        down_idx = 0

        for module in self.encoder:
            if isinstance(module, ResidualBlock):
                x = module(x, time_emb)
            elif isinstance(module, AttentionBlock):
                x = module(x)
            skips.append(x)

            # Check if next is downsample
            if down_idx < len(self.downsample):
                if len(skips) > 1 and skips[-1].shape == skips[-2].shape:
                    x = self.downsample[down_idx](x)
                    skips.append(x)
                    down_idx += 1

        # Bottleneck
        for module in self.bottleneck:
            if isinstance(module, ResidualBlock):
                x = module(x, time_emb)
            else:
                x = module(x)

        # Decoder with skip connections
        up_idx = 0
        for module in self.decoder:
            if isinstance(module, ResidualBlock):
                skip = skips.pop() if skips else torch.zeros_like(x)
                x = torch.cat([x, skip], dim=1)
                x = module(x, time_emb)
            elif isinstance(module, AttentionBlock):
                x = module(x)

            # Upsample
            if up_idx < len(self.upsample) and x.shape[-1] < 64:
                x = self.upsample[up_idx](x)
                up_idx += 1

        # Final convolution
        x = self.final(x)

        return x

# =============================================================================
# Simplified U-Net (for faster training/testing)
# =============================================================================

class SimpleFlowUNet(nn.Module):
    """
    Simplified U-Net for Flow Matching.

    A smaller, faster version suitable for experimentation and
    educational purposes. Uses fewer layers and channels.

    Architecture: 64 -> 128 -> 256 -> 128 -> 64
    """

    def __init__(self, in_channels=3, base_channels=64, time_emb_dim=128):
        super().__init__()

        self.in_channels = in_channels

        # Initial convolution: expand from 3 channels to base_channels
        # This avoids GroupNorm issues with 3-channel input
        self.init_conv = nn.Conv2d(in_channels, base_channels, kernel_size=3, padding=1)

        # Timestep embedding
        self.time_embedding = nn.Sequential(
            SinusoidalPositionEmbeddings(base_channels),
            nn.Linear(base_channels, time_emb_dim),
            nn.SiLU(),
            nn.Linear(time_emb_dim, time_emb_dim)
        )

        # Encoder (now starts from base_channels)
        self.enc1 = ResidualBlock(base_channels, base_channels, time_emb_dim)
        self.enc2 = ResidualBlock(base_channels, base_channels * 2, time_emb_dim)
        self.enc3 = ResidualBlock(base_channels * 2, base_channels * 4, time_emb_dim)

        self.down1 = Downsample(base_channels)
        self.down2 = Downsample(base_channels * 2)

        # Bottleneck with attention
        self.bottleneck = nn.Sequential(
            ResidualBlock(base_channels * 4, base_channels * 4, time_emb_dim),
            AttentionBlock(base_channels * 4),
        )

        # Decoder
        self.up1 = Upsample(base_channels * 4)
        self.up2 = Upsample(base_channels * 2)

        self.dec1 = ResidualBlock(base_channels * 4 + base_channels * 2, base_channels * 2, time_emb_dim)
        self.dec2 = ResidualBlock(base_channels * 2 + base_channels, base_channels, time_emb_dim)
        self.dec3 = ResidualBlock(base_channels + base_channels, base_channels, time_emb_dim)

        # Output
        self.final = nn.Sequential(
            nn.GroupNorm(8, base_channels),
            nn.SiLU(),
            nn.Conv2d(base_channels, in_channels, kernel_size=3, padding=1)
        )

    def forward(self, x, t):
        """Predict velocity v(x_t, t)."""
        time_emb = self.time_embedding(t)

        # Initial convolution: 3 channels -> base_channels
        x = self.init_conv(x)
        skip0 = x  # Now base_channels, compatible with GroupNorm

        # Encoder
        x = self.enc1(x, time_emb)
        skip1 = x
        x = self.down1(x)

        x = self.enc2(x, time_emb)
        skip2 = x
        x = self.down2(x)

        x = self.enc3(x, time_emb)

        # Bottleneck
        for module in self.bottleneck:
            if isinstance(module, ResidualBlock):
                x = module(x, time_emb)
            else:
                x = module(x)

        # Decoder
        x = self.up1(x)
        x = self.dec1(torch.cat([x, skip2], dim=1), time_emb)

        x = self.up2(x)
        x = self.dec2(torch.cat([x, skip1], dim=1), time_emb)

        x = self.dec3(torch.cat([x, skip0], dim=1), time_emb)

        return self.final(x)

# =============================================================================
# Model Utilities
# =============================================================================

def count_parameters(model):
    """Count the number of trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_model(model_type='simple', **kwargs):
    """
    Factory function to create Flow Matching models.

    Parameters:
        model_type: 'simple' for faster training, 'full' for best quality
        **kwargs: Additional arguments passed to model constructor

    Returns:
        FlowMatchingUNet or SimpleFlowUNet instance
    """
    if model_type == 'simple':
        return SimpleFlowUNet(**kwargs)
    elif model_type == 'full':
        return FlowMatchingUNet(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

# =============================================================================
# Testing
# =============================================================================

if __name__ == '__main__':
    print("Flow Matching U-Net Model")
    print("=" * 50)

    # Test simple model
    print("\nSimple U-Net:")
    model = SimpleFlowUNet(in_channels=3, base_channels=64)
    print(f"  Parameters: {count_parameters(model):,}")

    # Test forward pass
    x = torch.randn(2, 3, 64, 64)
    t = torch.rand(2)
    with torch.no_grad():
        v = model(x, t)
    print(f"  Input shape:  {x.shape}")
    print(f"  Time shape:   {t.shape}")
    print(f"  Output shape: {v.shape}")

    # Test full model
    print("\nFull U-Net:")
    model_full = FlowMatchingUNet(in_channels=3, base_channels=64)
    print(f"  Parameters: {count_parameters(model_full):,}")

    print("\nModel architecture is compatible with DDPM!")
    print("Key difference: predicts velocity v(x,t) instead of noise epsilon(x,t)")
