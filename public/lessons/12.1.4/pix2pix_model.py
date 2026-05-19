import torch
import torch.nn as nn

# Model configuration
IMG_SIZE = 256          # Input/output image size (256x256)
IMG_CHANNELS = 3        # RGB images
LATENT_CHANNELS = 512   # Maximum channels in bottleneck

class UNetDown(nn.Module):
    """
    U-Net Encoder Block (Downsampling)

    Applies: Conv2d -> BatchNorm (optional) -> LeakyReLU

    Each block halves the spatial dimensions while increasing channels.
    Example: 256x256x64 -> 128x128x128

    Args:
        in_channels: Number of input channels
        out_channels: Number of output channels
        normalize: Whether to apply BatchNorm (False for first layer)
    """

    def __init__(self, in_channels, out_channels, normalize=True):
        super().__init__()

        layers = [
            # Strided convolution halves spatial size
            # kernel=4, stride=2, padding=1 -> output = input/2
            nn.Conv2d(in_channels, out_channels, kernel_size=4,
                      stride=2, padding=1, bias=False)
        ]

        if normalize:
            layers.append(nn.BatchNorm2d(out_channels))

        layers.append(nn.LeakyReLU(0.2, inplace=True))

        self.model = nn.Sequential(*layers)

    def forward(self, x):
        return self.model(x)

class UNetUp(nn.Module):
    """
    U-Net Decoder Block (Upsampling with Skip Connection)

    Applies: ConvTranspose2d -> BatchNorm -> Dropout (optional) -> ReLU

    Each block doubles the spatial dimensions.
    Skip connections concatenate encoder features with decoder features.
    Example: 64x64x512 (+ 64x64x512 skip) -> 128x128x256

    Args:
        in_channels: Number of input channels (includes skip connection)
        out_channels: Number of output channels
        dropout: Whether to apply 50% dropout (used in first 3 decoder layers)
    """

    def __init__(self, in_channels, out_channels, dropout=False):
        super().__init__()

        layers = [
            # Transposed convolution doubles spatial size
            # kernel=4, stride=2, padding=1 -> output = input*2
            nn.ConvTranspose2d(in_channels, out_channels, kernel_size=4,
                               stride=2, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
        ]

        if dropout:
            layers.append(nn.Dropout(0.5))

        layers.append(nn.ReLU(inplace=True))

        self.model = nn.Sequential(*layers)

    def forward(self, x, skip_input):
        """
        Forward pass with skip connection.

        Args:
            x: Decoder feature map from previous layer
            skip_input: Encoder feature map to concatenate

        Returns:
            Upsampled features concatenated with skip connection
        """
        x = self.model(x)
        # Concatenate along channel dimension
        x = torch.cat([x, skip_input], dim=1)
        return x

class Generator(nn.Module):
    """
    U-Net Generator for Pix2Pix

    Transforms a 256x256 input image (sketch) into a 256x256 output image (colorized).

    Architecture:
        Encoder (8 layers):
            256x256x3 -> 128x128x64 -> 64x64x128 -> 32x32x256 ->
            16x16x512 -> 8x8x512 -> 4x4x512 -> 2x2x512 -> 1x1x512

        Decoder (8 layers with skip connections):
            1x1x512 -> 2x2x1024 -> 4x4x1024 -> 8x8x1024 ->
            16x16x1024 -> 32x32x512 -> 64x64x256 -> 128x128x128 -> 256x256x3

    Skip Connections:
        - enc1 (128x128x64) connects to dec7
        - enc2 (64x64x128) connects to dec6
        - enc3 (32x32x256) connects to dec5
        - enc4 (16x16x512) connects to dec4
        - enc5 (8x8x512) connects to dec3
        - enc6 (4x4x512) connects to dec2
        - enc7 (2x2x512) connects to dec1

    Why U-Net?
        Skip connections allow the decoder to access fine spatial details
        from the encoder, essential for pixel-aligned colorization.
        Without skip connections, the bottleneck would lose spatial information.
    """

    def __init__(self, in_channels=IMG_CHANNELS, out_channels=IMG_CHANNELS):
        super().__init__()

        # Encoder layers (downsampling)
        # Each layer halves spatial dimensions and increases channels

        # 256x256x3 -> 128x128x64 (no BatchNorm on first layer)
        self.down1 = UNetDown(in_channels, 64, normalize=False)
        # 128x128x64 -> 64x64x128
        self.down2 = UNetDown(64, 128)
        # 64x64x128 -> 32x32x256
        self.down3 = UNetDown(128, 256)
        # 32x32x256 -> 16x16x512
        self.down4 = UNetDown(256, 512)
        # 16x16x512 -> 8x8x512
        self.down5 = UNetDown(512, 512)
        # 8x8x512 -> 4x4x512
        self.down6 = UNetDown(512, 512)
        # 4x4x512 -> 2x2x512
        self.down7 = UNetDown(512, 512)
        # 2x2x512 -> 1x1x512 (bottleneck)
        self.down8 = UNetDown(512, 512, normalize=False)

        # Decoder layers (upsampling with skip connections)
        # Each layer doubles spatial dimensions
        # Input channels = previous layer + skip connection

        # 1x1x512 -> 2x2x512 (then concatenate with down7: 2x2x1024)
        self.up1 = UNetUp(512, 512, dropout=True)
        # 2x2x1024 -> 4x4x512 (then concatenate with down6: 4x4x1024)
        self.up2 = UNetUp(1024, 512, dropout=True)
        # 4x4x1024 -> 8x8x512 (then concatenate with down5: 8x8x1024)
        self.up3 = UNetUp(1024, 512, dropout=True)
        # 8x8x1024 -> 16x16x512 (then concatenate with down4: 16x16x1024)
        self.up4 = UNetUp(1024, 512)
        # 16x16x1024 -> 32x32x256 (then concatenate with down3: 32x32x512)
        self.up5 = UNetUp(1024, 256)
        # 32x32x512 -> 64x64x128 (then concatenate with down2: 64x64x256)
        self.up6 = UNetUp(512, 128)
        # 64x64x256 -> 128x128x64 (then concatenate with down1: 128x128x128)
        self.up7 = UNetUp(256, 64)

        # Final layer: 128x128x128 -> 256x256x3
        self.final = nn.Sequential(
            nn.ConvTranspose2d(128, out_channels, kernel_size=4,
                               stride=2, padding=1),
            nn.Tanh()  # Output in [-1, 1] range
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights using normal distribution (std=0.02)."""
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d)):
            nn.init.normal_(module.weight, 0.0, 0.02)
        elif isinstance(module, nn.BatchNorm2d):
            nn.init.normal_(module.weight, 1.0, 0.02)
            nn.init.constant_(module.bias, 0)

    def forward(self, x):
        """
        Generate output image from input sketch.

        Args:
            x: Input tensor of shape (batch, 3, 256, 256)
               Values should be normalized to [-1, 1]

        Returns:
            Output tensor of shape (batch, 3, 256, 256)
            Values in [-1, 1] range
        """
        # Encoder path - store outputs for skip connections
        d1 = self.down1(x)   # 128x128x64
        d2 = self.down2(d1)  # 64x64x128
        d3 = self.down3(d2)  # 32x32x256
        d4 = self.down4(d3)  # 16x16x512
        d5 = self.down5(d4)  # 8x8x512
        d6 = self.down6(d5)  # 4x4x512
        d7 = self.down7(d6)  # 2x2x512
        d8 = self.down8(d7)  # 1x1x512 (bottleneck)

        # Decoder path - use skip connections
        u1 = self.up1(d8, d7)  # 2x2x1024
        u2 = self.up2(u1, d6)  # 4x4x1024
        u3 = self.up3(u2, d5)  # 8x8x1024
        u4 = self.up4(u3, d4)  # 16x16x1024
        u5 = self.up5(u4, d3)  # 32x32x512
        u6 = self.up6(u5, d2)  # 64x64x256
        u7 = self.up7(u6, d1)  # 128x128x128

        return self.final(u7)  # 256x256x3

class PatchDiscriminator(nn.Module):
    """
    PatchGAN Discriminator (70x70 receptive field)

    Instead of classifying the entire image as real or fake, PatchGAN
    classifies each 70x70 overlapping patch independently. This focuses
    the discriminator on high-frequency structure and local texture.

    Architecture:
        Input: Concatenated (sketch, colorized) = 6 channels
        Layer 1: 256x256x6 -> 128x128x64 (no BatchNorm)
        Layer 2: 128x128x64 -> 64x64x128
        Layer 3: 64x64x128 -> 32x32x256
        Layer 4: 32x32x256 -> 31x31x512
        Layer 5: 31x31x512 -> 30x30x1 (output)

    Output: 30x30 grid where each cell represents real/fake probability
            for a 70x70 receptive field patch.

    Why PatchGAN?
        1. More detail-aware: Focuses on local texture quality
        2. Faster training: Fewer parameters than full-image discriminator
        3. Scale-independent: Works on any image size
        4. Better gradients: Multiple loss signals per image
    """

    def __init__(self, in_channels=IMG_CHANNELS):
        super().__init__()

        # Input is concatenated (sketch, target/generated) = 6 channels
        input_channels = in_channels * 2

        self.model = nn.Sequential(
            # Layer 1: 256x256x6 -> 128x128x64 (no BatchNorm)
            nn.Conv2d(input_channels, 64, kernel_size=4, stride=2, padding=1),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 2: 128x128x64 -> 64x64x128
            nn.Conv2d(64, 128, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 3: 64x64x128 -> 32x32x256
            nn.Conv2d(128, 256, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 4: 32x32x256 -> 31x31x512 (stride=1 to increase receptive field)
            nn.Conv2d(256, 512, kernel_size=4, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 5: 31x31x512 -> 30x30x1 (output layer)
            nn.Conv2d(512, 1, kernel_size=4, stride=1, padding=1)
            # No sigmoid - using BCEWithLogitsLoss for numerical stability
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights using normal distribution (std=0.02)."""
        if isinstance(module, nn.Conv2d):
            nn.init.normal_(module.weight, 0.0, 0.02)
        elif isinstance(module, nn.BatchNorm2d):
            nn.init.normal_(module.weight, 1.0, 0.02)
            nn.init.constant_(module.bias, 0)

    def forward(self, sketch, target):
        """
        Classify whether (sketch, target) pair is real or fake.

        Args:
            sketch: Input sketch tensor (batch, 3, 256, 256)
            target: Target/generated image tensor (batch, 3, 256, 256)

        Returns:
            Patch predictions tensor (batch, 1, 30, 30)
            Each cell is the logit for real/fake classification of that patch.
        """
        # Concatenate sketch and target along channel dimension
        x = torch.cat([sketch, target], dim=1)  # (batch, 6, 256, 256)
        return self.model(x)

def count_parameters(model):
    """Count total trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

if __name__ == '__main__':
    """Test the Pix2Pix model components."""
    print("=" * 60)
    print("Testing Pix2Pix Model Components")
    print("=" * 60)
    print()

    # Create models
    generator = Generator()
    discriminator = PatchDiscriminator()

    # Test input
    batch_size = 2
    sketch = torch.randn(batch_size, 3, 256, 256)

    # Test Generator
    print("Generator Test:")
    print(f"  Input shape:  {sketch.shape}")
    with torch.no_grad():
        fake_output = generator(sketch)
    print(f"  Output shape: {fake_output.shape}")
    print(f"  Output range: [{fake_output.min():.2f}, {fake_output.max():.2f}]")
    print(f"  Parameters:   {count_parameters(generator):,}")
    print()

    # Test Discriminator
    print("Discriminator Test:")
    print(f"  Sketch shape: {sketch.shape}")
    print(f"  Target shape: {fake_output.shape}")
    with torch.no_grad():
        disc_output = discriminator(sketch, fake_output)
    print(f"  Output shape: {disc_output.shape}")
    print(f"  Output meaning: {disc_output.shape[2]}x{disc_output.shape[3]} patch predictions")
    print(f"  Parameters:   {count_parameters(discriminator):,}")
    print()

    print("All tests passed successfully!")
    print()
    print("Architecture Summary:")
    print(f"  Generator:     U-Net with skip connections")
    print(f"  Discriminator: PatchGAN (70x70 receptive field)")
    print(f"  Input size:    256x256 RGB")
    print(f"  Output size:   256x256 RGB")
