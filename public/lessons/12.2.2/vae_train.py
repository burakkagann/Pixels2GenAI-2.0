import os
import numpy as np
import torch
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt

from vae_model import VAE, vae_loss, LATENT_DIM

# Training hyperparameters
BATCH_SIZE = 64
NUM_EPOCHS = 100
LEARNING_RATE = 0.0003
BETA = 1.0  # KL divergence weight (beta-VAE parameter)
NUM_TRAINING_IMAGES = 2000  # Number of procedural patterns to generate
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class AbstractArtDataset(Dataset):
    """
    Dataset of procedurally generated abstract art patterns.

    Generates diverse patterns using techniques from earlier modules:
    - Gradient fills (linear, radial, angular)
    - Geometric shapes (circles, rectangles)
    - Noise-based textures
    - Color field compositions
    """

    def __init__(self, num_images=NUM_TRAINING_IMAGES, img_size=64):
        self.num_images = num_images
        self.img_size = img_size
        print(f"Generating {num_images} training patterns...")
        self.patterns = [self._generate_pattern() for _ in range(num_images)]
        print("Done generating patterns.")

    def _generate_pattern(self):
        """Generate a single abstract pattern."""
        size = self.img_size
        pattern_type = np.random.choice([
            'gradient', 'circles', 'noise', 'stripes',
            'checker', 'radial', 'composite'
        ])

        # Create RGB canvas
        img = np.zeros((size, size, 3), dtype=np.float32)

        # Generate base color palette
        color1 = np.random.rand(3)
        color2 = np.random.rand(3)
        color3 = np.random.rand(3)

        # Create coordinate grids
        y, x = np.mgrid[0:size, 0:size].astype(np.float32) / size

        if pattern_type == 'gradient':
            # Linear gradient in random direction
            angle = np.random.rand() * 2 * np.pi
            t = (np.cos(angle) * x + np.sin(angle) * y + 1) / 2
            for c in range(3):
                img[:, :, c] = color1[c] * t + color2[c] * (1 - t)

        elif pattern_type == 'circles':
            # Concentric circles from random center
            cx, cy = np.random.rand(2)
            r = np.sqrt((x - cx)**2 + (y - cy)**2)
            freq = np.random.randint(3, 8)
            t = (np.sin(r * freq * np.pi * 2) + 1) / 2
            for c in range(3):
                img[:, :, c] = color1[c] * t + color2[c] * (1 - t)

        elif pattern_type == 'noise':
            # Smooth noise pattern using scaled random values
            scale = np.random.randint(4, 16)
            small = np.random.rand(scale, scale, 3).astype(np.float32)
            # Upsample with bilinear interpolation
            from scipy.ndimage import zoom
            img = zoom(small, (size/scale, size/scale, 1), order=1)
            img = np.clip(img, 0, 1)

        elif pattern_type == 'stripes':
            # Parallel stripes
            angle = np.random.rand() * np.pi
            freq = np.random.randint(4, 12)
            t = np.cos(angle) * x + np.sin(angle) * y
            stripe = (np.sin(t * freq * np.pi * 2) + 1) / 2
            for c in range(3):
                img[:, :, c] = color1[c] * stripe + color2[c] * (1 - stripe)

        elif pattern_type == 'checker':
            # Checkerboard pattern
            freq = np.random.randint(2, 8)
            check = ((x * freq).astype(int) + (y * freq).astype(int)) % 2
            for c in range(3):
                img[:, :, c] = np.where(check, color1[c], color2[c])

        elif pattern_type == 'radial':
            # Radial burst pattern
            cx, cy = 0.5 + (np.random.rand(2) - 0.5) * 0.3
            angle_grid = np.arctan2(y - cy, x - cx)
            freq = np.random.randint(6, 16)
            t = (np.sin(angle_grid * freq) + 1) / 2
            for c in range(3):
                img[:, :, c] = color1[c] * t + color2[c] * (1 - t)

        else:  # composite
            # Combine multiple patterns
            angle = np.random.rand() * 2 * np.pi
            t = (np.cos(angle) * x + np.sin(angle) * y + 1) / 2
            for c in range(3):
                img[:, :, c] = color1[c] * t + color2[c] * (1 - t)

            cx, cy = np.random.rand(2)
            r = np.sqrt((x - cx)**2 + (y - cy)**2)
            circle_mask = (r < 0.3).astype(np.float32)
            for c in range(3):
                img[:, :, c] = img[:, :, c] * (1 - circle_mask * 0.5) + \
                               color3[c] * circle_mask * 0.5

        img = np.clip(img, 0, 1)
        return img

    def __len__(self):
        return self.num_images

    def __getitem__(self, idx):
        img = self.patterns[idx]
        img_tensor = torch.from_numpy(img).permute(2, 0, 1)  # HWC -> CHW
        img_tensor = img_tensor * 2 - 1  # [0,1] -> [-1,1]
        return img_tensor

def train_vae(num_epochs=NUM_EPOCHS, save_samples_every=10):
    """
    Train the VAE on abstract art patterns.

    Args:
        num_epochs: Number of training epochs
        save_samples_every: Save sample images every N epochs
    """
    print(f"Training VAE on {DEVICE}")
    print(f"Latent dimension: {LATENT_DIM}")
    print("=" * 50)

    # Create dataset and dataloader
    dataset = AbstractArtDataset(NUM_TRAINING_IMAGES)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # Initialize model
    vae = VAE(latent_dim=LATENT_DIM).to(DEVICE)
    optimizer = optim.Adam(vae.parameters(), lr=LEARNING_RATE)

    # Fixed latent vectors for tracking progress
    fixed_z = torch.randn(16, LATENT_DIM, device=DEVICE)

    # Training history
    train_losses = []
    recon_losses = []
    kl_losses = []

    for epoch in range(num_epochs):
        vae.train()
        epoch_loss = 0
        epoch_recon = 0
        epoch_kl = 0

        for batch_idx, images in enumerate(dataloader):
            images = images.to(DEVICE)

            # Forward pass
            optimizer.zero_grad()
            reconstructed, mu, logvar = vae(images)

            # Compute loss
            loss, recon_loss, kl_loss = vae_loss(
                reconstructed, images, mu, logvar, beta=BETA
            )

            # Backward pass
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            epoch_recon += recon_loss.item()
            epoch_kl += kl_loss.item()

        # Average losses for epoch
        num_batches = len(dataloader)
        avg_loss = epoch_loss / num_batches
        avg_recon = epoch_recon / num_batches
        avg_kl = epoch_kl / num_batches

        train_losses.append(avg_loss)
        recon_losses.append(avg_recon)
        kl_losses.append(avg_kl)

        # Print progress
        print(f"Epoch [{epoch+1}/{num_epochs}] | "
              f"Loss: {avg_loss:.4f} | Recon: {avg_recon:.4f} | KL: {avg_kl:.4f}")

        # Save sample images
        if (epoch + 1) % save_samples_every == 0 or epoch == 0:
            save_samples(vae, fixed_z, epoch + 1)

    # Save the trained model
    torch.save(vae.state_dict(), 'vae_weights.pth')
    print("\nVAE weights saved to vae_weights.pth")

    # Plot training losses
    plot_losses(train_losses, recon_losses, kl_losses)

    return vae

def save_samples(vae, fixed_z, epoch):
    """Save a grid of generated samples."""
    vae.eval()
    with torch.no_grad():
        samples = vae.decoder(fixed_z).cpu()
    vae.train()

    # Convert to displayable format
    samples = (samples + 1) / 2  # [-1,1] -> [0,1]
    samples = samples.clamp(0, 1)

    # Create grid
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i, ax in enumerate(axes.flat):
        img = samples[i].permute(1, 2, 0).numpy()
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle(f'VAE Samples - Epoch {epoch}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'vae_samples_epoch_{epoch:03d}.png', dpi=100)
    plt.close()

def plot_losses(train_losses, recon_losses, kl_losses):
    """Plot training loss curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Total loss
    ax1.plot(train_losses, label='Total Loss', color='blue')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('VAE Training Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Decomposed losses
    ax2.plot(recon_losses, label='Reconstruction Loss', color='green')
    ax2.plot(kl_losses, label='KL Divergence', color='red')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.set_title('Loss Components')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('vae_training_losses.png', dpi=150)
    plt.close()
    print("Training loss plot saved to vae_training_losses.png")

if __name__ == '__main__':
    try:
        from scipy.ndimage import zoom
    except ImportError:
        print("Installing scipy for pattern generation...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'scipy'])

    train_vae(num_epochs=NUM_EPOCHS)
