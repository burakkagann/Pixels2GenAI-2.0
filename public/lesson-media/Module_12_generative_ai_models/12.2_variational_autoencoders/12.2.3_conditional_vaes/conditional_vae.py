import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

# ============================================================================
# Configuration
# ============================================================================

# Device selection: use GPU if available for faster training
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Model hyperparameters
IMAGE_SIZE = 28 * 28      # MNIST images are 28x28 pixels
LATENT_DIM = 16           # Dimensionality of latent space
HIDDEN_DIM = 256          # Hidden layer size
NUM_CLASSES = 10          # Digits 0-9

# Training hyperparameters
BATCH_SIZE = 128
NUM_EPOCHS = 50           # Reduced for faster training, increase for better quality
LEARNING_RATE = 1e-3

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# ============================================================================
# Neural Network Components
# ============================================================================

class Encoder(nn.Module):
    """
    Encoder network: Maps input image + class label to latent distribution.

    The encoder takes a flattened image concatenated with a one-hot label
    and outputs the mean (mu) and log-variance (logvar) of the latent
    distribution. This allows the model to learn label-specific representations.
    """

    def __init__(self, input_dim, hidden_dim, latent_dim, num_classes):
        super(Encoder, self).__init__()

        # Input is image pixels + one-hot encoded label
        self.input_layer = nn.Linear(input_dim + num_classes, hidden_dim)
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim)

        # Output mean and log-variance for the latent distribution
        self.mu_layer = nn.Linear(hidden_dim, latent_dim)
        self.logvar_layer = nn.Linear(hidden_dim, latent_dim)

        self.activation = nn.ReLU()

    def forward(self, x, labels_onehot):
        """
        Forward pass through encoder.

        Args:
            x: Flattened image tensor of shape (batch_size, 784)
            labels_onehot: One-hot encoded labels of shape (batch_size, 10)

        Returns:
            mu: Mean of latent distribution (batch_size, latent_dim)
            logvar: Log-variance of latent distribution (batch_size, latent_dim)
        """
        # Concatenate image with label information
        combined = torch.cat([x, labels_onehot], dim=1)

        # Pass through network
        hidden = self.activation(self.input_layer(combined))
        hidden = self.activation(self.hidden_layer(hidden))

        # Compute distribution parameters
        mu = self.mu_layer(hidden)
        logvar = self.logvar_layer(hidden)

        return mu, logvar

class Decoder(nn.Module):
    """
    Decoder network: Maps latent vector + class label to reconstructed image.

    The decoder takes a latent vector concatenated with a one-hot label
    and generates a reconstruction of the input image. The label tells
    the decoder which digit class to generate.
    """

    def __init__(self, latent_dim, hidden_dim, output_dim, num_classes):
        super(Decoder, self).__init__()

        # Input is latent vector + one-hot encoded label
        self.input_layer = nn.Linear(latent_dim + num_classes, hidden_dim)
        self.hidden_layer = nn.Linear(hidden_dim, hidden_dim)
        self.output_layer = nn.Linear(hidden_dim, output_dim)

        self.activation = nn.ReLU()

    def forward(self, z, labels_onehot):
        """
        Forward pass through decoder.

        Args:
            z: Latent vector of shape (batch_size, latent_dim)
            labels_onehot: One-hot encoded labels of shape (batch_size, 10)

        Returns:
            reconstruction: Reconstructed image of shape (batch_size, 784)
        """
        # Concatenate latent vector with label information
        combined = torch.cat([z, labels_onehot], dim=1)

        # Pass through network
        hidden = self.activation(self.input_layer(combined))
        hidden = self.activation(self.hidden_layer(hidden))

        # Generate reconstruction (sigmoid to keep values in [0, 1])
        reconstruction = torch.sigmoid(self.output_layer(hidden))

        return reconstruction

class ConditionalVAE(nn.Module):
    """
    Conditional Variational Autoencoder combining Encoder and Decoder.

    The CVAE extends the standard VAE by conditioning both the encoder
    and decoder on class labels. This allows controlled generation:
    you can sample from the latent space and specify which digit to generate.
    """

    def __init__(self, input_dim, hidden_dim, latent_dim, num_classes):
        super(ConditionalVAE, self).__init__()

        self.latent_dim = latent_dim
        self.num_classes = num_classes

        self.encoder = Encoder(input_dim, hidden_dim, latent_dim, num_classes)
        self.decoder = Decoder(latent_dim, hidden_dim, input_dim, num_classes)

    def reparameterize(self, mu, logvar):
        """
        Reparameterization trick: sample z = mu + std * epsilon

        This allows gradients to flow through the sampling operation.
        Instead of sampling directly from N(mu, sigma), we sample epsilon
        from N(0, 1) and compute z = mu + sigma * epsilon.

        Args:
            mu: Mean of the latent distribution
            logvar: Log-variance of the latent distribution

        Returns:
            z: Sampled latent vector
        """
        std = torch.exp(0.5 * logvar)  # Standard deviation
        epsilon = torch.randn_like(std)  # Random noise from N(0, 1)
        z = mu + std * epsilon
        return z

    def forward(self, x, labels):
        """
        Forward pass: encode, sample, decode.

        Args:
            x: Input images (batch_size, 784)
            labels: Integer class labels (batch_size,)

        Returns:
            reconstruction: Reconstructed images
            mu: Latent mean (for loss computation)
            logvar: Latent log-variance (for loss computation)
        """
        # Convert labels to one-hot encoding
        labels_onehot = torch.zeros(labels.size(0), self.num_classes, device=x.device)
        labels_onehot.scatter_(1, labels.unsqueeze(1), 1)

        # Encode: image + label -> latent distribution
        mu, logvar = self.encoder(x, labels_onehot)

        # Sample from latent distribution
        z = self.reparameterize(mu, logvar)

        # Decode: latent + label -> reconstruction
        reconstruction = self.decoder(z, labels_onehot)

        return reconstruction, mu, logvar

    def generate(self, labels, num_samples=1):
        """
        Generate new samples conditioned on specified labels.

        This is the key feature of Conditional VAEs: you can control
        what digit to generate by specifying the label.

        Args:
            labels: Integer labels specifying which digits to generate
            num_samples: Number of samples per label (if labels is scalar)

        Returns:
            samples: Generated images of shape (num_samples, 784)
        """
        self.eval()
        with torch.no_grad():
            if isinstance(labels, int):
                labels = torch.full((num_samples,), labels, dtype=torch.long, device=device)
            elif not isinstance(labels, torch.Tensor):
                labels = torch.tensor(labels, dtype=torch.long, device=device)

            # Create one-hot encoding
            labels_onehot = torch.zeros(labels.size(0), self.num_classes, device=device)
            labels_onehot.scatter_(1, labels.unsqueeze(1), 1)

            # Sample from standard normal prior
            z = torch.randn(labels.size(0), self.latent_dim, device=device)

            # Decode with specified labels
            samples = self.decoder(z, labels_onehot)

        return samples

# ============================================================================
# Loss Function
# ============================================================================

def vae_loss(reconstruction, original, mu, logvar):
    """
    Compute the VAE loss: Reconstruction Loss + KL Divergence.

    The VAE objective consists of two terms:
    1. Reconstruction loss: How well does the decoder reconstruct the input?
    2. KL divergence: How close is the latent distribution to the prior N(0,1)?

    Args:
        reconstruction: Reconstructed images from decoder
        original: Original input images
        mu: Mean of the latent distribution from encoder
        logvar: Log-variance of the latent distribution from encoder

    Returns:
        total_loss: Combined loss (to minimize)
        recon_loss: Reconstruction component (for monitoring)
        kl_loss: KL divergence component (for monitoring)
    """
    # Reconstruction loss: Binary Cross Entropy
    # Measures pixel-wise difference between original and reconstruction
    recon_loss = nn.functional.binary_cross_entropy(
        reconstruction, original, reduction='sum'
    )

    # KL Divergence: Regularizes latent space toward N(0, 1)
    # Formula: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

    total_loss = recon_loss + kl_loss

    return total_loss, recon_loss, kl_loss

# ============================================================================
# Data Loading
# ============================================================================

def load_mnist_data():
    """Load MNIST dataset with proper transforms."""
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])

    train_dataset = datasets.MNIST(
        root='./data',
        train=True,
        transform=transform,
        download=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    return train_loader

# ============================================================================
# Training
# ============================================================================

def train_cvae(model, train_loader, num_epochs):
    """
    Train the Conditional VAE model.

    Args:
        model: ConditionalVAE instance
        train_loader: DataLoader for training data
        num_epochs: Number of training epochs

    Returns:
        history: Dictionary containing loss history
    """
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    history = {
        'total_loss': [],
        'recon_loss': [],
        'kl_loss': []
    }

    model.train()

    for epoch in range(num_epochs):
        epoch_total_loss = 0
        epoch_recon_loss = 0
        epoch_kl_loss = 0
        num_batches = 0

        for batch_idx, (images, labels) in enumerate(train_loader):
            # Flatten images and move to device
            images = images.view(-1, IMAGE_SIZE).to(device)
            labels = labels.to(device)

            # Forward pass
            optimizer.zero_grad()
            reconstruction, mu, logvar = model(images, labels)

            # Compute loss
            total_loss, recon_loss, kl_loss = vae_loss(
                reconstruction, images, mu, logvar
            )

            # Backward pass
            total_loss.backward()
            optimizer.step()

            # Accumulate losses
            epoch_total_loss += total_loss.item()
            epoch_recon_loss += recon_loss.item()
            epoch_kl_loss += kl_loss.item()
            num_batches += 1

        # Average losses over epoch
        avg_total = epoch_total_loss / len(train_loader.dataset)
        avg_recon = epoch_recon_loss / len(train_loader.dataset)
        avg_kl = epoch_kl_loss / len(train_loader.dataset)

        history['total_loss'].append(avg_total)
        history['recon_loss'].append(avg_recon)
        history['kl_loss'].append(avg_kl)

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{num_epochs}] "
                  f"Total: {avg_total:.4f}, "
                  f"Recon: {avg_recon:.4f}, "
                  f"KL: {avg_kl:.4f}")

    return history

# ============================================================================
# Visualization
# ============================================================================

def generate_samples_grid(model, num_samples_per_class=10):
    """
    Generate a grid of samples for each digit class.

    Creates a 10x10 grid where each row contains samples of one digit (0-9).
    """
    model.eval()

    fig, axes = plt.subplots(10, num_samples_per_class, figsize=(12, 12))

    with torch.no_grad():
        for digit in range(10):
            # Generate samples for this digit
            labels = torch.full((num_samples_per_class,), digit, dtype=torch.long, device=device)
            samples = model.generate(labels)
            samples = samples.cpu().numpy()

            for i in range(num_samples_per_class):
                ax = axes[digit, i]
                ax.imshow(samples[i].reshape(28, 28), cmap='gray')
                ax.axis('off')

                # Add digit label on the left
                if i == 0:
                    ax.set_ylabel(str(digit), fontsize=14, rotation=0, labelpad=15)

    plt.suptitle('Conditional VAE Generated Digits\n(Each row shows samples conditioned on one digit class)',
                 fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig('cvae_generated_samples.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved cvae_generated_samples.png")

def visualize_conditional_generation(model):
    """
    Visualize how the same latent vector produces different digits with different labels.

    This demonstrates the core idea of conditional generation: the same random
    noise produces different outputs depending on the label you provide.
    """
    model.eval()

    fig, axes = plt.subplots(2, 10, figsize=(15, 4))

    with torch.no_grad():
        # Use the same random latent vector for all digits
        z_fixed = torch.randn(1, LATENT_DIM, device=device)

        for digit in range(10):
            # Create one-hot label
            labels_onehot = torch.zeros(1, NUM_CLASSES, device=device)
            labels_onehot[0, digit] = 1

            # Generate with fixed z but different label
            sample = model.decoder(z_fixed, labels_onehot)
            sample = sample.cpu().numpy().reshape(28, 28)

            # First row: generated images
            axes[0, digit].imshow(sample, cmap='gray')
            axes[0, digit].axis('off')
            axes[0, digit].set_title(str(digit), fontsize=12)

        # Second row: different random z for comparison
        for digit in range(10):
            z_random = torch.randn(1, LATENT_DIM, device=device)
            labels_onehot = torch.zeros(1, NUM_CLASSES, device=device)
            labels_onehot[0, digit] = 1

            sample = model.decoder(z_random, labels_onehot)
            sample = sample.cpu().numpy().reshape(28, 28)

            axes[1, digit].imshow(sample, cmap='gray')
            axes[1, digit].axis('off')

    axes[0, 0].set_ylabel('Same z', fontsize=11, rotation=0, labelpad=30)
    axes[1, 0].set_ylabel('Random z', fontsize=11, rotation=0, labelpad=30)

    plt.suptitle('Conditional Generation: Same Noise (top) vs Different Noise (bottom)',
                 fontsize=13, y=1.05)
    plt.tight_layout()
    plt.savefig('cvae_conditional_generation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved cvae_conditional_generation.png")

def plot_training_history(history):
    """Plot loss curves during training."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    epochs = range(1, len(history['total_loss']) + 1)

    # Total loss
    axes[0].plot(epochs, history['total_loss'], 'b-', linewidth=2)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Total Loss')
    axes[0].set_title('Total VAE Loss')
    axes[0].grid(True, alpha=0.3)

    # Reconstruction loss
    axes[1].plot(epochs, history['recon_loss'], 'g-', linewidth=2)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Reconstruction Loss')
    axes[1].set_title('Reconstruction Loss')
    axes[1].grid(True, alpha=0.3)

    # KL divergence
    axes[2].plot(epochs, history['kl_loss'], 'r-', linewidth=2)
    axes[2].set_xlabel('Epoch')
    axes[2].set_ylabel('KL Divergence')
    axes[2].set_title('KL Divergence Loss')
    axes[2].grid(True, alpha=0.3)

    plt.suptitle('Conditional VAE Training Progress', fontsize=14)
    plt.tight_layout()
    plt.savefig('cvae_training_history.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved cvae_training_history.png")

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Conditional VAE Training on MNIST")
    print("=" * 60)

    # Load data
    print("\nLoading MNIST dataset...")
    train_loader = load_mnist_data()
    print(f"Dataset loaded: {len(train_loader.dataset)} training samples")

    # Create model
    print("\nCreating Conditional VAE model...")
    model = ConditionalVAE(
        input_dim=IMAGE_SIZE,
        hidden_dim=HIDDEN_DIM,
        latent_dim=LATENT_DIM,
        num_classes=NUM_CLASSES
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"Model created with {total_params:,} parameters")

    # Train model
    print(f"\nTraining for {NUM_EPOCHS} epochs...")
    history = train_cvae(model, train_loader, NUM_EPOCHS)
    print("Training complete!")

    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_samples_grid(model)
    visualize_conditional_generation(model)
    plot_training_history(history)

    print("\n" + "=" * 60)
    print("All outputs saved successfully!")
    print("=" * 60)
