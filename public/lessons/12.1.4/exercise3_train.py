import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image
from glob import glob

from pix2pix_model import Generator, PatchDiscriminator

# Training Configuration
DATASET_PATH = 'anime_processed'          # Output from preprocess_anime_sketches.py
BATCH_SIZE = 4                             # Reduce if GPU memory is limited
NUM_EPOCHS = 100                           # Full training (reduce for quick test)
LEARNING_RATE = 0.0002                     # Adam learning rate
BETA1 = 0.5                                # Adam beta1 parameter
LAMBDA_L1 = 100                            # Weight for L1 reconstruction loss
IMG_SIZE = 256                             # Input/output image size

# Checkpoint epochs
CHECKPOINT_EPOCHS = [10, 25, 50, 75, 100]

# Sample indices for visualization (set to None for random, or specify 4 indices)
# Review anime_processed/sketches/ and select appropriate images
SAMPLE_INDICES = [14105, 14092, 14029, 13730]  # User-selected appropriate images

# Device configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class AnimeSketchDataset(Dataset):
    """
    Dataset loader for paired anime sketch-color images.

    Expects two folders:
    - anime_processed/sketches/  (input sketches)
    - anime_processed/colors/    (target colorized images)

    Each pair has the same filename (e.g., 00001.png in both folders).
    """

    def __init__(self, data_path, transform=None):
        """
        Initialize the dataset.

        Args:
            data_path: Path to anime_processed/ folder
            transform: Optional torchvision transforms
        """
        self.data_path = Path(data_path)
        self.sketch_dir = self.data_path / 'sketches'
        self.color_dir = self.data_path / 'colors'

        # Verify directories exist
        if not self.sketch_dir.exists() or not self.color_dir.exists():
            raise FileNotFoundError(
                f"Dataset directories not found at '{data_path}'.\n"
                f"Please run preprocess_anime_sketches.py first."
            )

        # Get list of images (sorted for consistent pairing)
        self.sketch_files = sorted(list(self.sketch_dir.glob('*.png')))
        self.color_files = sorted(list(self.color_dir.glob('*.png')))

        if len(self.sketch_files) != len(self.color_files):
            raise ValueError(
                f"Mismatched counts: {len(self.sketch_files)} sketches, "
                f"{len(self.color_files)} colors"
            )

        self.transform = transform

    def __len__(self):
        return len(self.sketch_files)

    def __getitem__(self, idx):
        """
        Load a sketch-color pair.

        Returns:
            sketch: Tensor (3, 256, 256) normalized to [-1, 1]
            color: Tensor (3, 256, 256) normalized to [-1, 1]
        """
        # Load images
        sketch = Image.open(self.sketch_files[idx]).convert('RGB')
        color = Image.open(self.color_files[idx]).convert('RGB')

        # Apply transforms
        if self.transform:
            sketch = self.transform(sketch)
            color = self.transform(color)

        return sketch, color

def get_transforms():
    """Create data transforms for training."""
    return transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # -> [-1, 1]
    ])

def train_epoch(generator, discriminator, dataloader,
                criterion_gan, criterion_l1,
                optimizer_g, optimizer_d, epoch):
    """
    Train for one epoch.

    Returns:
        Tuple of (avg_g_loss, avg_d_loss) for the epoch
    """
    g_losses = []
    d_losses = []

    for i, (sketch, real_color) in enumerate(dataloader):
        batch_size = sketch.size(0)
        sketch = sketch.to(DEVICE)
        real_color = real_color.to(DEVICE)

        # Labels for real/fake
        real_label = torch.ones(batch_size, 1, 30, 30, device=DEVICE)
        fake_label = torch.zeros(batch_size, 1, 30, 30, device=DEVICE)

        # ==================
        # Train Discriminator
        # ==================
        optimizer_d.zero_grad()

        # Generate fake colors
        fake_color = generator(sketch)

        # Discriminator on real pairs
        pred_real = discriminator(sketch, real_color)
        loss_d_real = criterion_gan(pred_real, real_label)

        # Discriminator on fake pairs
        pred_fake = discriminator(sketch, fake_color.detach())
        loss_d_fake = criterion_gan(pred_fake, fake_label)

        # Total discriminator loss
        loss_d = (loss_d_real + loss_d_fake) / 2
        loss_d.backward()
        optimizer_d.step()

        # ===============
        # Train Generator
        # ===============
        optimizer_g.zero_grad()

        # Generator wants discriminator to think fakes are real
        pred_fake = discriminator(sketch, fake_color)
        loss_g_gan = criterion_gan(pred_fake, real_label)

        # L1 loss for pixel-level reconstruction
        loss_g_l1 = criterion_l1(fake_color, real_color) * LAMBDA_L1

        # Total generator loss
        loss_g = loss_g_gan + loss_g_l1
        loss_g.backward()
        optimizer_g.step()

        # Record losses
        g_losses.append(loss_g.item())
        d_losses.append(loss_d.item())

    return np.mean(g_losses), np.mean(d_losses)

def save_samples(generator, fixed_sketches, epoch, output_dir='.'):
    """
    Save sample colorizations at checkpoint.

    Args:
        generator: Trained generator
        fixed_sketches: Fixed batch of sketches for consistent comparison
        epoch: Current epoch number
        output_dir: Directory to save images
    """
    generator.eval()

    with torch.no_grad():
        fake_colors = generator(fixed_sketches)

    # Convert to displayable format
    fake_colors = (fake_colors + 1) / 2  # [-1,1] -> [0,1]
    fake_colors = fake_colors.clamp(0, 1)
    sketches = (fixed_sketches + 1) / 2
    sketches = sketches.clamp(0, 1)

    # Create grid
    n_samples = min(4, fake_colors.size(0))
    fig, axes = plt.subplots(2, n_samples, figsize=(4*n_samples, 8))

    for i in range(n_samples):
        # Sketch (input)
        sketch_img = sketches[i].cpu().permute(1, 2, 0).numpy()
        axes[0, i].imshow(sketch_img)
        axes[0, i].set_title('Input Sketch', fontsize=10)
        axes[0, i].axis('off')

        # Colorized (output)
        color_img = fake_colors[i].cpu().permute(1, 2, 0).numpy()
        axes[1, i].imshow(color_img)
        axes[1, i].set_title('Colorized', fontsize=10)
        axes[1, i].axis('off')

    plt.suptitle(f'Pix2Pix Training - Epoch {epoch}', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_path = Path(output_dir) / f'exercise3_epoch_{epoch}.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    generator.train()
    print(f"  Saved: {output_path}")

def plot_training_progress(g_losses, d_losses, output_path='exercise3_training_progress.png'):
    """Plot and save training loss curves."""
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(g_losses, label='Generator Loss', color='blue', alpha=0.7)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Generator Loss')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(d_losses, label='Discriminator Loss', color='red', alpha=0.7)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Discriminator Loss')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.suptitle('Pix2Pix Training Progress', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")

def main():
    """Main training function."""
    print("=" * 60)
    print("Exercise 3: Train Pix2Pix on Anime Sketch Colorization")
    print("=" * 60)
    print()

    # Check for dataset
    if not Path(DATASET_PATH).exists():
        print(f"Error: Dataset not found at '{DATASET_PATH}'")
        print()
        print("Please complete these steps first:")
        print("1. Download the dataset from Kaggle:")
        print("   https://www.kaggle.com/datasets/ktaebum/anime-sketch-colorization-pair")
        print("2. Extract to 'anime_sketch_dataset/' folder")
        print("3. Run: python preprocess_anime_sketches.py")
        print("4. Then run this script again")
        return

    # Print configuration
    print(f"Device: {DEVICE}")
    print(f"Epochs: {NUM_EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"L1 weight (lambda): {LAMBDA_L1}")
    print()

    # Create dataset and dataloader
    print("Loading dataset...")
    transform = get_transforms()
    dataset = AnimeSketchDataset(DATASET_PATH, transform=transform)
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    print(f"Dataset size: {len(dataset)} pairs")
    print(f"Batches per epoch: {len(dataloader)}")
    print()

    # Initialize models
    print("Initializing models...")
    generator = Generator().to(DEVICE)
    discriminator = PatchDiscriminator().to(DEVICE)

    g_params = sum(p.numel() for p in generator.parameters())
    d_params = sum(p.numel() for p in discriminator.parameters())
    print(f"Generator parameters: {g_params:,}")
    print(f"Discriminator parameters: {d_params:,}")
    print()

    # Loss functions
    criterion_gan = nn.BCEWithLogitsLoss()  # For PatchGAN output
    criterion_l1 = nn.L1Loss()               # For pixel reconstruction

    # Optimizers
    optimizer_g = optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(BETA1, 0.999))
    optimizer_d = optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(BETA1, 0.999))

    # Fixed samples for visualization
    if SAMPLE_INDICES is not None:
        # Use specific indices for appropriate content
        fixed_sketches = []
        for idx in SAMPLE_INDICES[:4]:
            sketch, _ = dataset[idx]
            fixed_sketches.append(sketch)
        fixed_sketches = torch.stack(fixed_sketches).to(DEVICE)
        print(f"Using sample indices: {SAMPLE_INDICES[:4]}")
    else:
        # Use random samples from first batch
        fixed_batch = next(iter(dataloader))
        fixed_sketches = fixed_batch[0][:4].to(DEVICE)

    # Training tracking
    all_g_losses = []
    all_d_losses = []

    print("Starting training...")
    print()

    try:
        for epoch in range(1, NUM_EPOCHS + 1):
            # Train one epoch
            g_loss, d_loss = train_epoch(
                generator, discriminator, dataloader,
                criterion_gan, criterion_l1,
                optimizer_g, optimizer_d, epoch
            )

            all_g_losses.append(g_loss)
            all_d_losses.append(d_loss)

            # Print progress
            print(f"Epoch [{epoch}/{NUM_EPOCHS}] | G Loss: {g_loss:.4f} | D Loss: {d_loss:.4f}")

            # Save checkpoints
            if epoch in CHECKPOINT_EPOCHS:
                save_samples(generator, fixed_sketches, epoch)

    except KeyboardInterrupt:
        print("\nTraining interrupted by user.")
        print("Saving current progress...")

    # Save final model
    torch.save(generator.state_dict(), 'generator_weights.pth')
    print("\nGenerator saved to: generator_weights.pth")

    torch.save(discriminator.state_dict(), 'discriminator_weights.pth')
    print("Discriminator saved to: discriminator_weights.pth")

    # Plot training progress
    plot_training_progress(all_g_losses, all_d_losses)

    # Generate final samples
    print("\nGenerating final samples...")
    generator.eval()
    with torch.no_grad():
        final_colors = generator(fixed_sketches)

    final_colors = (final_colors + 1) / 2
    final_colors = final_colors.clamp(0, 1)
    sketches = (fixed_sketches + 1) / 2
    sketches = sketches.clamp(0, 1)

    # Save final comparison
    n_samples = 4
    fig, axes = plt.subplots(2, n_samples, figsize=(16, 8))

    for i in range(n_samples):
        sketch_img = sketches[i].cpu().permute(1, 2, 0).numpy()
        axes[0, i].imshow(sketch_img)
        axes[0, i].set_title('Input Sketch', fontsize=12, fontweight='bold')
        axes[0, i].axis('off')

        color_img = final_colors[i].cpu().permute(1, 2, 0).numpy()
        axes[1, i].imshow(color_img)
        axes[1, i].set_title('Colorized Output', fontsize=12, fontweight='bold')
        axes[1, i].axis('off')

    plt.suptitle(f'Final Results After {len(all_g_losses)} Epochs', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('exercise3_final_samples.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: exercise3_final_samples.png")

    print()
    print("=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print()
    print("Output files:")
    print("  - generator_weights.pth (trained model)")
    print("  - discriminator_weights.pth (optional)")
    print("  - exercise3_training_progress.png (loss curves)")
    print("  - exercise3_final_samples.png (final results)")
    print("  - exercise3_epoch_*.png (checkpoint samples)")
    print()
    print("Next steps:")
    print("  1. Run exercise1_observe.py to test your trained model")
    print("  2. Try exercise2_explore.py to explore model capabilities")
    print("  3. See Challenge Extensions in README.rst for advanced experiments")

if __name__ == '__main__':
    main()
