import torch
import torch.nn as nn

# Configuration constants
LATENT_DIM = 64      # Dimension of latent space
IMAGE_SIZE = 64      # Height and width of images
IMAGE_CHANNELS = 3   # RGB channels
FEATURE_MAPS = 64    # Base number of feature maps

class Encoder(nn.Module):
    """
    Encodes images into latent space parameters (mean and log-variance).

    Architecture:
        64x64x3 -> 32x32x64 -> 16x16x128 -> 8x8x256 -> 4x4x512 -> FC -> (mu, logvar)
    """

    def __init__(self, latent_dim=LATENT_DIM):
        super().__init__()

        # Convolutional layers progressively reduce spatial dimensions
        self.conv_layers = nn.Sequential(
            # Layer 1: 64x64x3 -> 32x32x64
            nn.Conv2d(IMAGE_CHANNELS, FEATURE_MAPS, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(FEATURE_MAPS),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 2: 32x32x64 -> 16x16x128
            nn.Conv2d(FEATURE_MAPS, FEATURE_MAPS * 2, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(FEATURE_MAPS * 2),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 3: 16x16x128 -> 8x8x256
            nn.Conv2d(FEATURE_MAPS * 2, FEATURE_MAPS * 4, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(FEATURE_MAPS * 4),
            nn.LeakyReLU(0.2, inplace=True),

            # Layer 4: 8x8x256 -> 4x4x512
            nn.Conv2d(FEATURE_MAPS * 4, FEATURE_MAPS * 8, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm2d(FEATURE_MAPS * 8),
            nn.LeakyReLU(0.2, inplace=True),
        )

        # Flatten and project to latent parameters
        # 4x4x512 = 8192 features
        self.flatten_size = FEATURE_MAPS * 8 * 4 * 4

        # Separate heads for mean and log-variance
        self.fc_mu = nn.Linear(self.flatten_size, latent_dim)
        self.fc_logvar = nn.Linear(self.flatten_size, latent_dim)

    def forward(self, x):
        """
        Encode input image to latent distribution parameters.

        Args:
            x: Input images of shape (batch, 3, 64, 64)

        Returns:
            mu: Mean of latent distribution (batch, latent_dim)
            logvar: Log-variance of latent distribution (batch, latent_dim)
        """
        # Pass through convolutional layers
        features = self.conv_layers(x)

        # Flatten spatial dimensions
        features = features.view(features.size(0), -1)

        # Compute distribution parameters
        mu = self.fc_mu(features)
        logvar = self.fc_logvar(features)

        return mu, logvar

class Decoder(nn.Module):
    """
    Decodes latent vectors back into images.

    Architecture:
        latent -> FC -> 4x4x512 -> 8x8x256 -> 16x16x128 -> 32x32x64 -> 64x64x3
    """

    def __init__(self, latent_dim=LATENT_DIM):
        super().__init__()

        # Project latent vector to spatial features
        self.fc = nn.Linear(latent_dim, FEATURE_MAPS * 8 * 4 * 4)

        # Transposed convolutions progressively increase spatial dimensions
        self.deconv_layers = nn.Sequential(
            # Layer 1: 4x4x512 -> 8x8x256
            nn.ConvTranspose2d(FEATURE_MAPS * 8, FEATURE_MAPS * 4,
                               kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(FEATURE_MAPS * 4),
            nn.ReLU(inplace=True),

            # Layer 2: 8x8x256 -> 16x16x128
            nn.ConvTranspose2d(FEATURE_MAPS * 4, FEATURE_MAPS * 2,
                               kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(FEATURE_MAPS * 2),
            nn.ReLU(inplace=True),

            # Layer 3: 16x16x128 -> 32x32x64
            nn.ConvTranspose2d(FEATURE_MAPS * 2, FEATURE_MAPS,
                               kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(FEATURE_MAPS),
            nn.ReLU(inplace=True),

            # Layer 4: 32x32x64 -> 64x64x3
            nn.ConvTranspose2d(FEATURE_MAPS, IMAGE_CHANNELS,
                               kernel_size=4, stride=2, padding=1, bias=False),
            nn.Tanh()  # Output in [-1, 1] range
        )

    def forward(self, z):
        """
        Decode latent vector to image.

        Args:
            z: Latent vectors of shape (batch, latent_dim)

        Returns:
            Reconstructed images of shape (batch, 3, 64, 64)
        """
        # Project to spatial features
        features = self.fc(z)
        features = features.view(features.size(0), FEATURE_MAPS * 8, 4, 4)

        # Upsample to full image
        output = self.deconv_layers(features)

        return output

class VAE(nn.Module):
    """
    Complete Variational Autoencoder combining Encoder and Decoder.

    The VAE learns a continuous latent space where nearby points produce
    similar outputs, enabling smooth interpolation for morphing animations.
    """

    def __init__(self, latent_dim=LATENT_DIM):
        super().__init__()
        self.latent_dim = latent_dim
        self.encoder = Encoder(latent_dim)
        self.decoder = Decoder(latent_dim)

    def reparameterize(self, mu, logvar):
        """
        Reparameterization trick: sample from N(mu, var) using N(0, 1).

        This trick allows gradients to flow through the sampling operation,
        enabling end-to-end training with backpropagation.

        Args:
            mu: Mean of the latent distribution
            logvar: Log-variance of the latent distribution

        Returns:
            Sampled latent vector z = mu + std * epsilon
        """
        # Convert log-variance to standard deviation
        std = torch.exp(0.5 * logvar)

        # Sample epsilon from standard normal
        epsilon = torch.randn_like(std)

        # Reparameterized sample
        z = mu + std * epsilon

        return z

    def forward(self, x):
        """
        Full forward pass: encode -> sample -> decode.

        Args:
            x: Input images of shape (batch, 3, 64, 64)

        Returns:
            reconstructed: Reconstructed images
            mu: Latent mean
            logvar: Latent log-variance
        """
        # Encode to latent distribution parameters
        mu, logvar = self.encoder(x)

        # Sample from the distribution
        z = self.reparameterize(mu, logvar)

        # Decode back to image
        reconstructed = self.decoder(z)

        return reconstructed, mu, logvar

    def sample(self, num_samples, device='cpu'):
        """
        Generate new images by sampling from the prior distribution.

        Args:
            num_samples: Number of images to generate
            device: Device to generate on ('cpu' or 'cuda')

        Returns:
            Generated images of shape (num_samples, 3, 64, 64)
        """
        # Sample from standard normal (prior)
        z = torch.randn(num_samples, self.latent_dim, device=device)

        # Decode to images
        with torch.no_grad():
            images = self.decoder(z)

        return images

    def encode_to_latent(self, x):
        """
        Encode images to latent vectors (using mean, not sampling).

        Useful for encoding real images to interpolate between them.

        Args:
            x: Input images of shape (batch, 3, 64, 64)

        Returns:
            Latent vectors (batch, latent_dim)
        """
        with torch.no_grad():
            mu, _ = self.encoder(x)
        return mu

def vae_loss(reconstructed, original, mu, logvar, beta=1.0):
    """
    Compute the VAE loss: reconstruction + KL divergence.

    The beta parameter controls the trade-off between reconstruction
    quality and latent space regularity (beta-VAE).

    Args:
        reconstructed: Reconstructed images from decoder
        original: Original input images
        mu: Latent mean from encoder
        logvar: Latent log-variance from encoder
        beta: Weight for KL divergence term (default: 1.0)

    Returns:
        total_loss: Combined loss
        recon_loss: Reconstruction loss (MSE)
        kl_loss: KL divergence loss
    """
    # Reconstruction loss (pixel-wise MSE)
    recon_loss = nn.functional.mse_loss(reconstructed, original, reduction='sum')
    recon_loss = recon_loss / original.size(0)  # Average over batch

    # KL divergence loss
    # KL(N(mu, var) || N(0, 1)) = -0.5 * sum(1 + log(var) - mu^2 - var)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    kl_loss = kl_loss / original.size(0)  # Average over batch

    # Total loss
    total_loss = recon_loss + beta * kl_loss

    return total_loss, recon_loss, kl_loss

# Test the model architecture
if __name__ == '__main__':
    print("Testing VAE architecture...")
    print(f"Latent dimension: {LATENT_DIM}")
    print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}x{IMAGE_CHANNELS}")
    print()

    # Create model
    vae = VAE(latent_dim=LATENT_DIM)

    # Count parameters
    total_params = sum(p.numel() for p in vae.parameters())
    print(f"Total parameters: {total_params:,}")

    # Test forward pass
    test_input = torch.randn(4, IMAGE_CHANNELS, IMAGE_SIZE, IMAGE_SIZE)
    reconstructed, mu, logvar = vae(test_input)

    print(f"\nForward pass test:")
    print(f"  Input shape: {test_input.shape}")
    print(f"  Reconstructed shape: {reconstructed.shape}")
    print(f"  Mu shape: {mu.shape}")
    print(f"  Logvar shape: {logvar.shape}")

    # Test sampling
    samples = vae.sample(4)
    print(f"\nSampling test:")
    print(f"  Generated samples shape: {samples.shape}")

    # Test loss
    loss, recon, kl = vae_loss(reconstructed, test_input, mu, logvar)
    print(f"\nLoss test:")
    print(f"  Total loss: {loss.item():.4f}")
    print(f"  Reconstruction loss: {recon.item():.4f}")
    print(f"  KL divergence: {kl.item():.4f}")

    print("\nAll tests passed!")
