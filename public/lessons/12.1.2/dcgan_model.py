"""
DCGAN Generator and Discriminator networks.

Architecture based on Radford et al. (2015) "Unsupervised Representation
Learning with Deep Convolutional Generative Adversarial Networks".

Implementation adapted from PyTorch Official DCGAN Tutorial:
https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html
BSD-3-Clause License

Educational modifications:
- Simplified for beginner-intermediate learners
- Adapted for abstract art generation (64x64 images)
- Removed advanced features not essential for core understanding
"""

import torch
import torch.nn as nn


# Model hyperparameters
LATENT_DIM = 100      # Size of random noise vector (z)
IMG_SIZE = 64         # Output image size (64x64 pixels)
IMG_CHANNELS = 3      # RGB images
FEATURE_MAP_SIZE = 64 # Base number of feature maps


class Generator(nn.Module):
    """
    DCGAN Generator Network

    Transforms a random latent vector (z) into a 64x64 RGB image.
    Uses transposed convolutions to upsample from a small spatial
    representation to the final image size.

    Architecture:
        z (100) -> 4x4x512 -> 8x8x256 -> 16x16x128 -> 32x32x64 -> 64x64x3

    Each layer (except the last) uses:
        - Transposed Convolution (ConvTranspose2d)
        - Batch Normalization
        - ReLU activation

    The final layer uses Tanh to output values in [-1, 1].
    """

    def __init__(self, latent_dim=LATENT_DIM, img_channels=IMG_CHANNELS,
                 feature_maps=FEATURE_MAP_SIZE):
        super(Generator, self).__init__()

        self.latent_dim = latent_dim

        # Build the generator network
        self.network = nn.Sequential(
            # Layer 1: z (100) -> 4x4x512
            # Input: latent vector of size (batch, latent_dim, 1, 1)
            nn.ConvTranspose2d(latent_dim, feature_maps * 8, 4, 1, 0, bias=False),
            nn.BatchNorm2d(feature_maps * 8),
            nn.ReLU(True),

            # Layer 2: 4x4x512 -> 8x8x256
            nn.ConvTranspose2d(feature_maps * 8, feature_maps * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 4),
            nn.ReLU(True),

            # Layer 3: 8x8x256 -> 16x16x128
            nn.ConvTranspose2d(feature_maps * 4, feature_maps * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 2),
            nn.ReLU(True),

            # Layer 4: 16x16x128 -> 32x32x64
            nn.ConvTranspose2d(feature_maps * 2, feature_maps, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps),
            nn.ReLU(True),

            # Layer 5: 32x32x64 -> 64x64x3 (output layer)
            nn.ConvTranspose2d(feature_maps, img_channels, 4, 2, 1, bias=False),
            nn.Tanh()  # Output in range [-1, 1]
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights as described in DCGAN paper."""
        if isinstance(module, (nn.ConvTranspose2d, nn.Conv2d)):
            nn.init.normal_(module.weight, 0.0, 0.02)
        elif isinstance(module, nn.BatchNorm2d):
            nn.init.normal_(module.weight, 1.0, 0.02)
            nn.init.constant_(module.bias, 0)

    def forward(self, z):
        """
        Generate images from latent vectors.

        Args:
            z: Tensor of shape (batch_size, latent_dim, 1, 1)

        Returns:
            Tensor of shape (batch_size, 3, 64, 64) with values in [-1, 1]
        """
        return self.network(z)


class Discriminator(nn.Module):
    """
    DCGAN Discriminator Network

    Takes a 64x64 RGB image and outputs a single value indicating
    whether the image is real or fake.

    Architecture:
        64x64x3 -> 32x32x64 -> 16x16x128 -> 8x8x256 -> 4x4x512 -> 1

    Each layer (except first and last) uses:
        - Strided Convolution (Conv2d)
        - Batch Normalization
        - LeakyReLU activation (slope=0.2)

    The first layer has no BatchNorm. The final layer uses Sigmoid.
    """

    def __init__(self, img_channels=IMG_CHANNELS, feature_maps=FEATURE_MAP_SIZE):
        super(Discriminator, self).__init__()

        self.network = nn.Sequential(
            # Layer 1: 64x64x3 -> 32x32x64 (no BatchNorm)
            nn.Conv2d(img_channels, feature_maps, 4, 2, 1, bias=False),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 2: 32x32x64 -> 16x16x128
            nn.Conv2d(feature_maps, feature_maps * 2, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 2),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 3: 16x16x128 -> 8x8x256
            nn.Conv2d(feature_maps * 2, feature_maps * 4, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 4),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 4: 8x8x256 -> 4x4x512
            nn.Conv2d(feature_maps * 4, feature_maps * 8, 4, 2, 1, bias=False),
            nn.BatchNorm2d(feature_maps * 8),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 5: 4x4x512 -> 1 (output layer)
            nn.Conv2d(feature_maps * 8, 1, 4, 1, 0, bias=False),
            nn.Sigmoid()  # Output probability in [0, 1]
        )

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights as described in DCGAN paper."""
        if isinstance(module, (nn.ConvTranspose2d, nn.Conv2d)):
            nn.init.normal_(module.weight, 0.0, 0.02)
        elif isinstance(module, nn.BatchNorm2d):
            nn.init.normal_(module.weight, 1.0, 0.02)
            nn.init.constant_(module.bias, 0)

    def forward(self, img):
        """
        Classify images as real or fake.

        Args:
            img: Tensor of shape (batch_size, 3, 64, 64) with values in [-1, 1]

        Returns:
            Tensor of shape (batch_size, 1, 1, 1) with probabilities
        """
        return self.network(img)


def count_parameters(model):
    """Count trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == '__main__':
    # Test the models
    print("Testing DCGAN Models")
    print("=" * 50)

    # Create models
    generator = Generator()
    discriminator = Discriminator()

    # Test generator
    z = torch.randn(4, LATENT_DIM, 1, 1)
    fake_images = generator(z)
    print(f"Generator input shape: {z.shape}")
    print(f"Generator output shape: {fake_images.shape}")
    print(f"Generator parameters: {count_parameters(generator):,}")

    # Test discriminator
    predictions = discriminator(fake_images)
    print(f"\nDiscriminator input shape: {fake_images.shape}")
    print(f"Discriminator output shape: {predictions.shape}")
    print(f"Discriminator parameters: {count_parameters(discriminator):,}")

    print("\nModel test completed successfully!")
