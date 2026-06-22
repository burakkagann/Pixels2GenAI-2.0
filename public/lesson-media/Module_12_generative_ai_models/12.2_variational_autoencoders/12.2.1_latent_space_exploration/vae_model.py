import torch
import torch.nn as nn

# Configuration constants
IMAGE_SIZE = 16
INPUT_DIM = IMAGE_SIZE * IMAGE_SIZE  # 256 pixels
HIDDEN_DIM = 128
LATENT_DIM = 8  # Dimensionality of the latent space

class Encoder(nn.Module):
    """
    Encoder network that maps input data to latent distribution parameters.

    The encoder outputs two vectors: mean (mu) and log-variance (log_var),
    which parameterize the approximate posterior distribution q(z|x).
    """

    def __init__(self, input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, latent_dim=LATENT_DIM):
        super().__init__()

        # Shared layers for feature extraction
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )

        # Separate heads for mean and log-variance
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_log_var = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x):
        """
        Encode input to latent distribution parameters.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            mu: Mean of latent distribution (batch_size, latent_dim)
            log_var: Log-variance of latent distribution (batch_size, latent_dim)
        """
        h = self.shared(x)
        mu = self.fc_mu(h)
        log_var = self.fc_log_var(h)
        return mu, log_var

class Decoder(nn.Module):
    """
    Decoder network that reconstructs data from latent samples.

    The decoder maps points in the latent space back to the data space,
    enabling generation of new samples by sampling from the latent distribution.
    """

    def __init__(self, latent_dim=LATENT_DIM, hidden_dim=HIDDEN_DIM, output_dim=INPUT_DIM):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid()  # Output in [0, 1] range for image pixels
        )

    def forward(self, z):
        """
        Decode latent vector to reconstructed data.

        Args:
            z: Latent vector of shape (batch_size, latent_dim)

        Returns:
            Reconstructed data of shape (batch_size, output_dim)
        """
        return self.network(z)

class VAE(nn.Module):
    """
    Variational Autoencoder combining encoder and decoder.

    The VAE learns a compressed representation (latent space) of the input data.
    It uses the reparameterization trick to enable backpropagation through
    the stochastic sampling step.

    Key components:
    - Encoder: Maps input x to distribution parameters (mu, log_var)
    - Reparameterization: Samples z = mu + std * epsilon
    - Decoder: Reconstructs x from z
    """

    def __init__(self, input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, latent_dim=LATENT_DIM):
        super().__init__()
        self.latent_dim = latent_dim
        self.encoder = Encoder(input_dim, hidden_dim, latent_dim)
        self.decoder = Decoder(latent_dim, hidden_dim, input_dim)

    def reparameterize(self, mu, log_var):
        """
        Reparameterization trick: sample z = mu + std * epsilon.

        This allows gradients to flow through the sampling operation
        by expressing the random variable z as a deterministic function
        of mu, log_var, and a noise variable epsilon.

        Args:
            mu: Mean of the latent distribution
            log_var: Log-variance of the latent distribution

        Returns:
            z: Sampled latent vector
        """
        std = torch.exp(0.5 * log_var)  # Standard deviation
        epsilon = torch.randn_like(std)  # Random noise from N(0, 1)
        z = mu + std * epsilon
        return z

    def forward(self, x):
        """
        Forward pass through the VAE.

        Args:
            x: Input data of shape (batch_size, input_dim)

        Returns:
            recon_x: Reconstructed data
            mu: Mean of latent distribution
            log_var: Log-variance of latent distribution
        """
        # Encode to latent distribution parameters
        mu, log_var = self.encoder(x)

        # Sample from the latent distribution
        z = self.reparameterize(mu, log_var)

        # Decode to reconstruct input
        recon_x = self.decoder(z)

        return recon_x, mu, log_var

    def encode(self, x):
        """Encode input to latent space (returns mean for deterministic encoding)."""
        mu, _ = self.encoder(x)
        return mu

    def decode(self, z):
        """Decode latent vector to data space."""
        return self.decoder(z)

    def sample(self, num_samples, device='cpu'):
        """
        Generate new samples by sampling from the prior p(z) = N(0, I).

        Args:
            num_samples: Number of samples to generate
            device: Device to create tensors on

        Returns:
            Generated samples of shape (num_samples, input_dim)
        """
        z = torch.randn(num_samples, self.latent_dim).to(device)
        return self.decode(z)

def vae_loss(recon_x, x, mu, log_var, beta=1.0):
    """
    Compute the VAE loss: reconstruction loss + KL divergence.

    The loss function is:
        L = E[log p(x|z)] - beta * KL(q(z|x) || p(z))

    Where:
    - Reconstruction loss measures how well the decoder reconstructs the input
    - KL divergence regularizes the latent space to be close to N(0, I)
    - Beta controls the trade-off (beta=1 is standard VAE, beta>1 is beta-VAE)

    Args:
        recon_x: Reconstructed data
        x: Original input data
        mu: Mean of latent distribution
        log_var: Log-variance of latent distribution
        beta: Weight for KL divergence term (default=1.0)

    Returns:
        total_loss: Combined loss
        recon_loss: Reconstruction component
        kl_loss: KL divergence component
    """
    # Reconstruction loss (binary cross-entropy for images in [0,1])
    recon_loss = nn.functional.binary_cross_entropy(recon_x, x, reduction='sum')

    # KL divergence: -0.5 * sum(1 + log_var - mu^2 - exp(log_var))
    kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())

    # Total loss
    total_loss = recon_loss + beta * kl_loss

    return total_loss, recon_loss, kl_loss

if __name__ == "__main__":
    # Quick test of the model
    print("Testing VAE model...")

    vae = VAE()
    print(f"VAE created with latent dimension: {vae.latent_dim}")

    # Test forward pass
    test_input = torch.randn(4, INPUT_DIM)
    recon, mu, log_var = vae(test_input)

    print(f"Input shape: {test_input.shape}")
    print(f"Reconstruction shape: {recon.shape}")
    print(f"Latent mu shape: {mu.shape}")
    print(f"Latent log_var shape: {log_var.shape}")

    # Test loss computation
    loss, recon_l, kl_l = vae_loss(recon, torch.sigmoid(test_input), mu, log_var)
    print(f"Total loss: {loss.item():.2f}")
    print(f"Reconstruction loss: {recon_l.item():.2f}")
    print(f"KL divergence: {kl_l.item():.2f}")

    # Test sampling
    samples = vae.sample(2)
    print(f"Generated samples shape: {samples.shape}")

    print("VAE model test passed!")
