import numpy as np
import torch
import torch.optim as optim
import matplotlib.pyplot as plt
from PIL import Image
import os

# Import VAE model from local module
from vae_model import VAE, vae_loss, IMAGE_SIZE, INPUT_DIM, LATENT_DIM

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Training configuration
BATCH_SIZE = 64
NUM_EPOCHS = 200
LEARNING_RATE = 0.001
NUM_PATTERNS = 1000

def generate_geometric_patterns(num_samples, image_size=IMAGE_SIZE):
    """
    Generate simple geometric patterns as training data.

    Creates four types of patterns:
    - Type 0: Diagonal line (top-left to bottom-right)
    - Type 1: Horizontal line (center)
    - Type 2: Vertical line (center)
    - Type 3: Cross (horizontal + vertical)

    Args:
        num_samples: Number of patterns to generate
        image_size: Size of square images

    Returns:
        patterns: Tensor of shape (num_samples, image_size * image_size)
        labels: Array of pattern type labels
    """
    patterns = []
    labels = []

    for i in range(num_samples):
        pattern = np.zeros((image_size, image_size), dtype=np.float32)
        pattern_type = i % 4  # Cycle through pattern types

        if pattern_type == 0:  # Diagonal
            for j in range(image_size):
                pattern[j, j] = 1.0
                if j > 0:
                    pattern[j, j - 1] = 0.5
                if j < image_size - 1:
                    pattern[j, j + 1] = 0.5
        elif pattern_type == 1:  # Horizontal
            mid = image_size // 2
            pattern[mid - 1:mid + 1, :] = 1.0
        elif pattern_type == 2:  # Vertical
            mid = image_size // 2
            pattern[:, mid - 1:mid + 1] = 1.0
        else:  # Cross
            mid = image_size // 2
            pattern[mid - 1:mid + 1, :] = 1.0
            pattern[:, mid - 1:mid + 1] = 1.0

        # Add slight noise for variation
        noise = np.random.randn(image_size, image_size) * 0.05
        pattern = np.clip(pattern + noise, 0, 1)

        patterns.append(pattern.flatten())
        labels.append(pattern_type)

    return torch.tensor(np.array(patterns), dtype=torch.float32), np.array(labels)

def train_vae(vae, train_data, num_epochs=NUM_EPOCHS, lr=LEARNING_RATE, save_progression=True):
    """
    Train the VAE on the provided data.

    Args:
        vae: VAE model
        train_data: Training data tensor
        num_epochs: Number of training epochs
        lr: Learning rate
        save_progression: Whether to save progression images

    Returns:
        losses: Dictionary with training history
        progression_images: List of reconstruction images at key epochs
    """
    optimizer = optim.Adam(vae.parameters(), lr=lr)
    losses = {'total': [], 'recon': [], 'kl': []}
    progression_images = []
    progression_epochs = [1, 50, 100, 150, 200]

    # Fixed samples for visualization
    fixed_samples = train_data[:8]

    print("Training VAE...")
    for epoch in range(1, num_epochs + 1):
        # Shuffle data
        perm = torch.randperm(len(train_data))
        train_data_shuffled = train_data[perm]

        epoch_loss = 0
        epoch_recon = 0
        epoch_kl = 0
        num_batches = 0

        # Mini-batch training
        for i in range(0, len(train_data), BATCH_SIZE):
            batch = train_data_shuffled[i:i + BATCH_SIZE]

            optimizer.zero_grad()
            recon, mu, log_var = vae(batch)
            loss, recon_loss, kl_loss = vae_loss(recon, batch, mu, log_var)

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            epoch_recon += recon_loss.item()
            epoch_kl += kl_loss.item()
            num_batches += 1

        # Record average losses
        losses['total'].append(epoch_loss / num_batches)
        losses['recon'].append(epoch_recon / num_batches)
        losses['kl'].append(epoch_kl / num_batches)

        # Save progression images at key epochs
        if save_progression and epoch in progression_epochs:
            with torch.no_grad():
                recon, _, _ = vae(fixed_samples)
                progression_images.append({
                    'epoch': epoch,
                    'original': fixed_samples.numpy(),
                    'reconstructed': recon.numpy()
                })

        # Print progress
        if epoch % 50 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}: Loss={losses['total'][-1]:.2f}, "
                  f"Recon={losses['recon'][-1]:.2f}, KL={losses['kl'][-1]:.2f}")

    print("Training complete!")
    return losses, progression_images

def visualize_latent_space(vae, data, labels, save_path='latent_space_visualization.png'):
    """
    Visualize the 2D projection of the latent space.

    For latent dimensions > 2, uses PCA to project to 2D.
    Points are colored by their pattern type.

    Args:
        vae: Trained VAE model
        data: Input data tensor
        labels: Pattern type labels
        save_path: Path to save the visualization
    """
    vae.eval()
    with torch.no_grad():
        # Encode all data to latent space
        mu, _ = vae.encoder(data)
        latent = mu.numpy()

    # If latent dim > 2, use first two dimensions (or PCA)
    if latent.shape[1] > 2:
        # Simple projection: use first two dimensions
        x = latent[:, 0]
        y = latent[:, 1]
    else:
        x = latent[:, 0]
        y = latent[:, 1]

    # Create visualization
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

    # Color map for pattern types
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']
    pattern_names = ['Diagonal', 'Horizontal', 'Vertical', 'Cross']

    for i in range(4):
        mask = labels == i
        ax.scatter(x[mask], y[mask], c=colors[i], label=pattern_names[i],
                   alpha=0.6, s=30, edgecolors='white', linewidth=0.5)

    ax.set_xlabel('Latent Dimension 1', fontsize=12)
    ax.set_ylabel('Latent Dimension 2', fontsize=12)
    ax.set_title('Latent Space Visualization', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def visualize_reconstructions(vae, data, save_path='reconstruction_comparison.png'):
    """
    Create a comparison grid of original vs reconstructed patterns.

    Args:
        vae: Trained VAE model
        data: Input data tensor
        save_path: Path to save the visualization
    """
    vae.eval()

    # Select 8 samples (2 of each type)
    samples = data[:8]

    with torch.no_grad():
        recon, _, _ = vae(samples)

    # Create grid: top row = originals, bottom row = reconstructions
    fig, axes = plt.subplots(2, 8, figsize=(16, 4), dpi=150)

    for i in range(8):
        # Original
        orig = samples[i].numpy().reshape(IMAGE_SIZE, IMAGE_SIZE)
        axes[0, i].imshow(orig, cmap='gray', vmin=0, vmax=1)
        axes[0, i].axis('off')
        if i == 0:
            axes[0, i].set_title('Originals', fontsize=12, fontweight='bold', loc='left')

        # Reconstruction
        rec = recon[i].numpy().reshape(IMAGE_SIZE, IMAGE_SIZE)
        axes[1, i].imshow(rec, cmap='gray', vmin=0, vmax=1)
        axes[1, i].axis('off')
        if i == 0:
            axes[1, i].set_title('Reconstructions', fontsize=12, fontweight='bold', loc='left')

    plt.suptitle('VAE Reconstruction Comparison', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def visualize_interpolation(vae, data, save_path='interpolation_sequence.png'):
    """
    Create an interpolation sequence between two patterns in latent space.

    This demonstrates that VAE latent spaces are continuous and meaningful:
    walking along a path in latent space produces smooth transitions.

    Args:
        vae: Trained VAE model
        data: Input data tensor
        save_path: Path to save the visualization
    """
    vae.eval()

    # Select two different patterns (diagonal and cross)
    start_idx = 0  # Diagonal
    end_idx = 3    # Cross
    start_pattern = data[start_idx:start_idx + 1]
    end_pattern = data[end_idx:end_idx + 1]

    with torch.no_grad():
        # Encode both patterns
        start_mu, _ = vae.encoder(start_pattern)
        end_mu, _ = vae.encoder(end_pattern)

        # Create interpolation steps
        num_steps = 8
        alphas = np.linspace(0, 1, num_steps)
        interpolated = []

        for alpha in alphas:
            # Linear interpolation in latent space
            z = (1 - alpha) * start_mu + alpha * end_mu
            # Decode
            decoded = vae.decode(z)
            interpolated.append(decoded.numpy().reshape(IMAGE_SIZE, IMAGE_SIZE))

    # Create visualization
    fig, axes = plt.subplots(1, num_steps, figsize=(16, 2), dpi=150)

    for i, (img, alpha) in enumerate(zip(interpolated, alphas)):
        axes[i].imshow(img, cmap='gray', vmin=0, vmax=1)
        axes[i].axis('off')
        axes[i].set_title(f'a={alpha:.2f}', fontsize=10)

    plt.suptitle('Latent Space Interpolation: Diagonal to Cross',
                 fontsize=14, fontweight='bold', y=1.1)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def visualize_training_progression(progression_images, save_path='training_progression.png'):
    """
    Visualize how reconstruction quality improves during training.

    Args:
        progression_images: List of dictionaries with epoch, original, reconstructed
        save_path: Path to save the visualization
    """
    num_epochs = len(progression_images)
    num_samples = 4  # Show 4 samples

    fig, axes = plt.subplots(num_epochs, num_samples, figsize=(8, 10), dpi=150)

    for row, prog in enumerate(progression_images):
        epoch = prog['epoch']
        for col in range(num_samples):
            recon = prog['reconstructed'][col].reshape(IMAGE_SIZE, IMAGE_SIZE)
            axes[row, col].imshow(recon, cmap='gray', vmin=0, vmax=1)
            axes[row, col].axis('off')
            if col == 0:
                axes[row, col].set_ylabel(f'Epoch {epoch}', fontsize=10, rotation=0,
                                          labelpad=40, ha='right', va='center')

    plt.suptitle('Reconstruction Quality During Training', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def create_architecture_diagram(save_path='vae_architecture.png'):
    """
    Create a diagram showing the VAE architecture.

    This diagram illustrates the encoder-decoder structure and the
    reparameterization trick in the latent space.
    """
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)

    # Colors
    encoder_color = '#3498db'
    latent_color = '#e74c3c'
    decoder_color = '#2ecc71'
    arrow_color = '#34495e'

    # Draw encoder block
    encoder = plt.Rectangle((0.5, 2), 2, 3, facecolor=encoder_color, edgecolor='black', linewidth=2)
    ax.add_patch(encoder)
    ax.text(1.5, 3.5, 'ENCODER', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(1.5, 3.0, 'Input: 16x16', ha='center', va='center', fontsize=9, color='white')

    # Draw latent space (two parallel paths for mu and sigma)
    mu_box = plt.Rectangle((4, 4), 1.5, 1.2, facecolor=latent_color, edgecolor='black', linewidth=2)
    sigma_box = plt.Rectangle((4, 1.8), 1.5, 1.2, facecolor=latent_color, edgecolor='black', linewidth=2)
    ax.add_patch(mu_box)
    ax.add_patch(sigma_box)
    ax.text(4.75, 4.6, 'mean (mu)', ha='center', va='center', fontsize=10, fontweight='bold', color='white')
    ax.text(4.75, 2.4, 'log_var', ha='center', va='center', fontsize=10, fontweight='bold', color='white')

    # Sampling box
    sample_circle = plt.Circle((7, 3.5), 0.8, facecolor='#f39c12', edgecolor='black', linewidth=2)
    ax.add_patch(sample_circle)
    ax.text(7, 3.5, 'z', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(7, 2.3, 'z = mu + std*e', ha='center', va='center', fontsize=8)

    # Draw decoder block
    decoder = plt.Rectangle((9, 2), 2, 3, facecolor=decoder_color, edgecolor='black', linewidth=2)
    ax.add_patch(decoder)
    ax.text(10, 3.5, 'DECODER', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    ax.text(10, 3.0, 'Output: 16x16', ha='center', va='center', fontsize=9, color='white')

    # Draw arrows
    # Input to encoder
    ax.annotate('', xy=(0.5, 3.5), xytext=(-0.5, 3.5),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))
    ax.text(-0.7, 3.5, 'Input\nImage', ha='right', va='center', fontsize=10)

    # Encoder to mu/sigma
    ax.annotate('', xy=(4, 4.6), xytext=(2.5, 4.0),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))
    ax.annotate('', xy=(4, 2.4), xytext=(2.5, 3.0),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))

    # Mu/sigma to z
    ax.annotate('', xy=(6.2, 3.7), xytext=(5.5, 4.6),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))
    ax.annotate('', xy=(6.2, 3.3), xytext=(5.5, 2.4),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))

    # Z to decoder
    ax.annotate('', xy=(9, 3.5), xytext=(7.8, 3.5),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))

    # Decoder to output
    ax.annotate('', xy=(12, 3.5), xytext=(11, 3.5),
                arrowprops=dict(arrowstyle='->', color=arrow_color, lw=2))
    ax.text(12.2, 3.5, 'Reconstructed\nImage', ha='left', va='center', fontsize=10)

    # Add latent space label
    ax.text(5.5, 6.5, 'LATENT SPACE', ha='center', va='center', fontsize=14,
            fontweight='bold', color=latent_color)
    latent_box = plt.Rectangle((3.5, 1.3), 4.5, 4.7, facecolor='none',
                                 edgecolor=latent_color, linewidth=2, linestyle='--')
    ax.add_patch(latent_box)

    # Epsilon arrow
    ax.annotate('', xy=(7, 4.3), xytext=(7, 5.5),
                arrowprops=dict(arrowstyle='->', color='#9b59b6', lw=2))
    ax.text(7, 5.8, 'epsilon ~ N(0,1)', ha='center', va='center', fontsize=9, color='#9b59b6')

    ax.set_xlim(-1.5, 13)
    ax.set_ylim(0.5, 7)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title('Variational Autoencoder Architecture', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Saved: {save_path}")

def main():
    """Main training and visualization pipeline."""
    print("=" * 60)
    print("Latent Space Exploration with VAE")
    print("=" * 60)

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Generate training data
    print("\nGenerating training data...")
    train_data, labels = generate_geometric_patterns(NUM_PATTERNS)
    print(f"Generated {NUM_PATTERNS} patterns of shape {IMAGE_SIZE}x{IMAGE_SIZE}")

    # Create and train VAE
    vae = VAE()
    print(f"Created VAE with latent dimension: {LATENT_DIM}")

    losses, progression = train_vae(vae, train_data, num_epochs=NUM_EPOCHS)

    # Generate all visualizations
    print("\nGenerating visualizations...")

    # Architecture diagram
    create_architecture_diagram('vae_architecture.png')

    # Latent space visualization
    visualize_latent_space(vae, train_data, labels, 'latent_space_visualization.png')

    # Reconstruction comparison
    visualize_reconstructions(vae, train_data, 'reconstruction_comparison.png')

    # Interpolation sequence
    visualize_interpolation(vae, train_data, 'interpolation_sequence.png')

    # Training progression
    visualize_training_progression(progression, 'training_progression.png')

    print("\n" + "=" * 60)
    print("All visualizations complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
