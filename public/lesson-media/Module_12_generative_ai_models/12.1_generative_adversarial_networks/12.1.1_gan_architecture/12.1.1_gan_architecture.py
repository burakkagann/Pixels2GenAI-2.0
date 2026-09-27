# GAN Architecture - Training Script
# Based on: "GANs in 50 lines of code" by Dev Nag
# Source: https://github.com/devnag/pytorch-generative-adversarial-networks
# License: MIT
#
# Adaptations for NumPy-to-GenAI:
# - Added detailed comments for educational clarity
# - Simplified variable names
# - Added visualization of training progress

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# Try to import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("matplotlib not available - will skip plotting")
    MATPLOTLIB_AVAILABLE = False

# =============================================================================
# Configuration
# =============================================================================
# Target distribution parameters (what we want the Generator to learn)
DATA_MEAN = 4.0          # Center of the target distribution
DATA_STDDEV = 1.25       # Spread of the target distribution

# Network architecture
G_INPUT_SIZE = 1         # Generator input: single random number
G_HIDDEN_SIZE = 5        # Generator hidden layer neurons
G_OUTPUT_SIZE = 1        # Generator output: single generated number

D_INPUT_SIZE = 500       # Discriminator sees batch statistics (4 moments)
D_HIDDEN_SIZE = 10       # Discriminator hidden layer neurons
D_OUTPUT_SIZE = 1        # Discriminator output: real/fake probability

# Training parameters
LEARNING_RATE = 1e-3     # How fast networks learn
SGD_MOMENTUM = 0.9       # Momentum for SGD optimizer
NUM_EPOCHS = 5000        # Total training iterations
PRINT_INTERVAL = 500     # How often to print progress
D_STEPS = 20             # Discriminator training steps per epoch
G_STEPS = 20             # Generator training steps per epoch

# =============================================================================
# Helper Functions
# =============================================================================
def sample_real_data(num_samples):
    """
    Sample from the real data distribution (Gaussian).
    This is what the Generator is trying to learn to produce.
    """
    samples = np.random.normal(DATA_MEAN, DATA_STDDEV, (1, num_samples))
    return torch.Tensor(samples)

def sample_noise(batch_size, noise_dim):
    """
    Sample random noise as input to the Generator.
    The Generator transforms this noise into fake data.
    """
    return torch.rand(batch_size, noise_dim)

def compute_moments(data):
    """
    Compute statistical moments of the data distribution.
    These statistics help the Discriminator distinguish real from fake.

    Returns: [mean, std, skewness, kurtosis]
    """
    mean = torch.mean(data)
    diffs = data - mean
    variance = torch.mean(torch.pow(diffs, 2.0))
    std = torch.pow(variance, 0.5)

    # Standardize before computing higher moments
    zscores = diffs / std
    skewness = torch.mean(torch.pow(zscores, 3.0))
    kurtosis = torch.mean(torch.pow(zscores, 4.0)) - 3.0  # Excess kurtosis

    # Combine into a single tensor
    moments = torch.cat([
        mean.reshape(1,),
        std.reshape(1,),
        skewness.reshape(1,),
        kurtosis.reshape(1,)
    ])
    return moments

# =============================================================================
# Neural Network Definitions
# =============================================================================
class Generator(nn.Module):
    """
    Generator network: transforms random noise into fake data.

    Architecture: Input -> Hidden -> Hidden -> Output
    Goal: Produce data that fools the Discriminator
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(Generator, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, output_size)
        self.activation = nn.Tanh()

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.activation(self.layer2(x))
        x = self.layer3(x)  # No activation on output
        return x

class Discriminator(nn.Module):
    """
    Discriminator network: classifies data as real or fake.

    Architecture: Input -> Hidden -> Hidden -> Output (probability)
    Goal: Correctly identify real vs fake data
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(Discriminator, self).__init__()
        self.layer1 = nn.Linear(input_size, hidden_size)
        self.layer2 = nn.Linear(hidden_size, hidden_size)
        self.layer3 = nn.Linear(hidden_size, output_size)
        self.activation = nn.Sigmoid()

    def forward(self, x):
        x = self.activation(self.layer1(x))
        x = self.activation(self.layer2(x))
        x = self.activation(self.layer3(x))  # Output probability [0, 1]
        return x

# =============================================================================
# Training Function
# =============================================================================
def train_gan():
    """
    Train the GAN using the adversarial training process.

    The training alternates between:
    1. Training the Discriminator to better classify real vs fake
    2. Training the Generator to better fool the Discriminator
    """
    # Initialize networks
    generator = Generator(G_INPUT_SIZE, G_HIDDEN_SIZE, G_OUTPUT_SIZE)
    discriminator = Discriminator(4, D_HIDDEN_SIZE, D_OUTPUT_SIZE)  # 4 moments as input

    # Loss function: Binary Cross Entropy
    criterion = nn.BCELoss()

    # Optimizers
    g_optimizer = optim.SGD(generator.parameters(), lr=LEARNING_RATE, momentum=SGD_MOMENTUM)
    d_optimizer = optim.SGD(discriminator.parameters(), lr=LEARNING_RATE, momentum=SGD_MOMENTUM)

    # Track losses for visualization
    g_losses = []
    d_losses = []

    print("Training GAN to generate numbers from N({}, {})".format(DATA_MEAN, DATA_STDDEV))
    print("=" * 60)

    for epoch in range(NUM_EPOCHS):
        # ---------------------------------------------------------------------
        # Train Discriminator
        # ---------------------------------------------------------------------
        for _ in range(D_STEPS):
            d_optimizer.zero_grad()

            # Train on REAL data (label = 1)
            real_data = sample_real_data(D_INPUT_SIZE)
            real_moments = compute_moments(real_data)
            real_prediction = discriminator(real_moments)
            real_label = torch.ones(1)
            d_loss_real = criterion(real_prediction, real_label)
            d_loss_real.backward()

            # Train on FAKE data (label = 0)
            noise = sample_noise(D_INPUT_SIZE, G_INPUT_SIZE)
            fake_data = generator(noise).detach()  # detach to avoid training G
            fake_moments = compute_moments(fake_data.t())
            fake_prediction = discriminator(fake_moments)
            fake_label = torch.zeros(1)
            d_loss_fake = criterion(fake_prediction, fake_label)
            d_loss_fake.backward()

            d_optimizer.step()

        # ---------------------------------------------------------------------
        # Train Generator
        # ---------------------------------------------------------------------
        for _ in range(G_STEPS):
            g_optimizer.zero_grad()

            # Generator wants Discriminator to output 1 (think fake is real)
            noise = sample_noise(D_INPUT_SIZE, G_INPUT_SIZE)
            fake_data = generator(noise)
            fake_moments = compute_moments(fake_data.t())
            fake_prediction = discriminator(fake_moments)
            target_label = torch.ones(1)  # Generator wants D to say "real"
            g_loss = criterion(fake_prediction, target_label)
            g_loss.backward()

            g_optimizer.step()

        # Record losses
        g_losses.append(g_loss.item())
        d_losses.append((d_loss_real.item() + d_loss_fake.item()) / 2)

        # Print progress
        if (epoch + 1) % PRINT_INTERVAL == 0:
            # Get statistics of generated data
            with torch.no_grad():
                test_noise = sample_noise(1000, G_INPUT_SIZE)
                generated = generator(test_noise).numpy().flatten()
                gen_mean = np.mean(generated)
                gen_std = np.std(generated)

            print("Epoch {:5d} | D Loss: {:.4f} | G Loss: {:.4f} | "
                  "Generated: mean={:.2f}, std={:.2f}".format(
                      epoch + 1, d_losses[-1], g_losses[-1], gen_mean, gen_std))

    print("=" * 60)
    print("Training complete!")
    print("Target distribution: mean={}, std={}".format(DATA_MEAN, DATA_STDDEV))

    return generator, discriminator, g_losses, d_losses

def visualize_results(generator, g_losses, d_losses):
    """Generate visualization of training results."""
    if not MATPLOTLIB_AVAILABLE:
        print("Skipping visualization (matplotlib not available)")
        return

    # Generate samples from trained generator
    with torch.no_grad():
        noise = sample_noise(10000, G_INPUT_SIZE)
        generated_samples = generator(noise).numpy().flatten()

    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Plot 1: Generated distribution vs target
    ax1 = axes[0]
    ax1.hist(generated_samples, bins=50, density=True, alpha=0.7, label='Generated')

    # Overlay true distribution
    x = np.linspace(DATA_MEAN - 4*DATA_STDDEV, DATA_MEAN + 4*DATA_STDDEV, 100)
    true_dist = (1/(DATA_STDDEV * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-DATA_MEAN)/DATA_STDDEV)**2)
    ax1.plot(x, true_dist, 'r-', linewidth=2, label='Target N({}, {})'.format(DATA_MEAN, DATA_STDDEV))

    ax1.set_xlabel('Value')
    ax1.set_ylabel('Density')
    ax1.set_title('Generated Distribution vs Target')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Loss curves
    ax2 = axes[1]
    epochs = range(1, len(g_losses) + 1)
    ax2.plot(epochs, d_losses, label='Discriminator Loss', alpha=0.8)
    ax2.plot(epochs, g_losses, label='Generator Loss', alpha=0.8)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.set_title('Training Loss Over Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('gan_training_results.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\nResults saved to 'gan_training_results.png'")
    print("Generated samples: mean={:.3f}, std={:.3f}".format(
        np.mean(generated_samples), np.std(generated_samples)))

# =============================================================================
# Main Execution
# =============================================================================
if __name__ == '__main__':
    # Train the GAN
    generator, discriminator, g_losses, d_losses = train_gan()

    # Visualize results
    visualize_results(generator, g_losses, d_losses)
