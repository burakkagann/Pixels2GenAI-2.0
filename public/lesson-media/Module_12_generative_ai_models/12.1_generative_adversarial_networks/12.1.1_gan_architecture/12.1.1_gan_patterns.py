# GAN Patterns - Visual Bridge to Image Generation
# Extends the number-generating GAN concept to simple visual patterns
# Prepares learners for DCGAN in Module 12.1.2

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt

# =============================================================================
# Configuration
# =============================================================================
IMAGE_SIZE = 8           # 8x8 pixel patterns (simple for fast training)
LATENT_DIM = 32          # Size of random noise input (increased for variety)
HIDDEN_DIM = 128         # Hidden layer size (increased capacity)
OUTPUT_DIM = IMAGE_SIZE * IMAGE_SIZE  # Flattened image size

# Training parameters
LEARNING_RATE = 0.0002   # Lower learning rate for stability
NUM_EPOCHS = 5000        # More epochs for better convergence
BATCH_SIZE = 64          # Larger batch for stable gradients
PRINT_INTERVAL = 500

# =============================================================================
# Data Generation - Simple Geometric Patterns
# =============================================================================
def generate_real_patterns(num_samples):
    """
    Generate simple geometric patterns as 'real' training data.

    Creates two types: horizontal lines and vertical lines.
    Each pattern is an 8x8 grayscale image.
    """
    patterns = []

    for _ in range(num_samples):
        pattern = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float32)
        pattern_type = np.random.randint(0, 2)

        if pattern_type == 0:
            # Horizontal line at random position
            row = np.random.randint(1, IMAGE_SIZE - 1)
            pattern[row, :] = 1.0
        else:
            # Vertical line at random position
            col = np.random.randint(1, IMAGE_SIZE - 1)
            pattern[:, col] = 1.0

        # Flatten and normalize to [-1, 1]
        patterns.append(pattern.flatten() * 2 - 1)

    return torch.tensor(np.array(patterns), dtype=torch.float32)

# =============================================================================
# Neural Networks
# =============================================================================
class Generator(nn.Module):
    """Generator: transforms random noise into 8x8 patterns."""

    def __init__(self):
        super(Generator, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(LATENT_DIM, HIDDEN_DIM),
            nn.BatchNorm1d(HIDDEN_DIM),
            nn.LeakyReLU(0.2),
            nn.Linear(HIDDEN_DIM, HIDDEN_DIM * 2),
            nn.BatchNorm1d(HIDDEN_DIM * 2),
            nn.LeakyReLU(0.2),
            nn.Linear(HIDDEN_DIM * 2, HIDDEN_DIM),
            nn.BatchNorm1d(HIDDEN_DIM),
            nn.LeakyReLU(0.2),
            nn.Linear(HIDDEN_DIM, OUTPUT_DIM),
            nn.Tanh()  # Output in [-1, 1]
        )

    def forward(self, z):
        return self.network(z)

class Discriminator(nn.Module):
    """Discriminator: classifies patterns as real or fake."""

    def __init__(self):
        super(Discriminator, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(OUTPUT_DIM, HIDDEN_DIM),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(HIDDEN_DIM, HIDDEN_DIM // 2),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(HIDDEN_DIM // 2, 1),
            nn.Sigmoid()  # Output probability [0, 1]
        )

    def forward(self, x):
        return self.network(x)

# =============================================================================
# Training
# =============================================================================
def train_pattern_gan():
    """Train the GAN to generate simple visual patterns."""

    # Initialize networks
    generator = Generator()
    discriminator = Discriminator()

    # Loss and optimizers (beta1=0.5 recommended for GANs)
    criterion = nn.BCELoss()
    g_optimizer = optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))
    d_optimizer = optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))

    print("Training GAN to generate {}x{} patterns".format(IMAGE_SIZE, IMAGE_SIZE))
    print("=" * 50)

    for epoch in range(NUM_EPOCHS):
        # Get real and fake data
        real_data = generate_real_patterns(BATCH_SIZE)
        noise = torch.randn(BATCH_SIZE, LATENT_DIM)
        fake_data = generator(noise)

        # Create labels for this batch
        real_label = torch.ones(BATCH_SIZE, 1)
        fake_label = torch.zeros(BATCH_SIZE, 1)

        # Train Discriminator
        d_optimizer.zero_grad()

        real_output = discriminator(real_data)
        d_loss_real = criterion(real_output, real_label)

        fake_output = discriminator(fake_data.detach())
        d_loss_fake = criterion(fake_output, fake_label)

        d_loss = (d_loss_real + d_loss_fake) / 2
        d_loss.backward()
        d_optimizer.step()

        # Train Generator (train twice per D step for balance)
        for _ in range(2):
            g_optimizer.zero_grad()
            noise = torch.randn(BATCH_SIZE, LATENT_DIM)
            fake_data = generator(noise)
            fake_output = discriminator(fake_data)
            g_loss = criterion(fake_output, real_label)
            g_loss.backward()
            g_optimizer.step()

        # Print progress
        if (epoch + 1) % PRINT_INTERVAL == 0:
            print("Epoch {:4d} | D Loss: {:.4f} | G Loss: {:.4f}".format(
                epoch + 1, d_loss.item(), g_loss.item()))

    print("=" * 50)
    print("Training complete!")

    return generator

def visualize_patterns(generator):
    """Generate and display sample patterns."""

    # Generate samples
    with torch.no_grad():
        noise = torch.randn(16, LATENT_DIM)
        generated = generator(noise).numpy()

    # Also generate some real patterns for comparison
    real = generate_real_patterns(8).numpy()

    # Create visualization
    fig, axes = plt.subplots(3, 8, figsize=(12, 5))

    # Row 1: Real patterns
    for i in range(8):
        img = real[i].reshape(IMAGE_SIZE, IMAGE_SIZE)
        axes[0, i].imshow(img, cmap='gray', vmin=-1, vmax=1)
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Real', fontsize=10)

    # Row 2-3: Generated patterns
    for i in range(8):
        img = generated[i].reshape(IMAGE_SIZE, IMAGE_SIZE)
        axes[1, i].imshow(img, cmap='gray', vmin=-1, vmax=1)
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Generated', fontsize=10)

    for i in range(8):
        img = generated[i + 8].reshape(IMAGE_SIZE, IMAGE_SIZE)
        axes[2, i].imshow(img, cmap='gray', vmin=-1, vmax=1)
        axes[2, i].axis('off')

    plt.suptitle('Real Patterns (top) vs Generated Patterns (bottom)', fontsize=12)
    plt.tight_layout()
    plt.savefig('gan_patterns_output.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\nResults saved to 'gan_patterns_output.png'")

# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    generator = train_pattern_gan()
    visualize_patterns(generator)
