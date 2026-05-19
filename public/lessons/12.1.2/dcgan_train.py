"""
Train a DCGAN on abstract art images.

Training loop based on PyTorch Official DCGAN Tutorial:
https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html
BSD-3-Clause License

Adapted for abstract art generation using pre-made dataset.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np

from dcgan_model import Generator, Discriminator, LATENT_DIM


# Hyperparameters
DATASET_PATH = 'abstract_art_dataset'
BATCH_SIZE = 64
NUM_EPOCHS = 50
LEARNING_RATE = 0.0002
BETA1 = 0.5  # Adam optimizer beta1 parameter
NUM_WORKERS = 2
IMG_SIZE = 64

# Device configuration
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def train_dcgan(dataset_path=DATASET_PATH, num_epochs=NUM_EPOCHS, batch_size=BATCH_SIZE):
    """
    Train the DCGAN on abstract art images.

    Args:
        dataset_path: Path to dataset folder
        num_epochs: Number of training epochs
        batch_size: Batch size for training
    """
    print("=" * 60)
    print("DCGAN Training on Abstract Art")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    print(f"Dataset: {dataset_path}")
    print(f"Epochs: {num_epochs}")
    print(f"Batch size: {batch_size}")
    print()

    # Create dataset and dataloader
    transform = transforms.Compose([
        transforms.Resize(IMG_SIZE),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # Normalize to [-1, 1]
    ])

    # Use ImageFolder which expects subdirectories (create a wrapper if needed)
    # For simplicity, we'll load images from a flat directory
    from glob import glob
    from PIL import Image as PILImage

    class FlatImageDataset(torch.utils.data.Dataset):
        def __init__(self, folder_path, transform=None):
            self.image_paths = sorted(glob(os.path.join(folder_path, '*.png')))
            self.transform = transform

        def __len__(self):
            return len(self.image_paths)

        def __getitem__(self, idx):
            img = PILImage.open(self.image_paths[idx]).convert('RGB')
            if self.transform:
                img = self.transform(img)
            return img, 0  # Return dummy label

    dataset = FlatImageDataset(dataset_path, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    print(f"Dataset loaded: {len(dataset)} images")
    print(f"Batches per epoch: {len(dataloader)}")
    print()

    # Create models
    generator = Generator().to(DEVICE)
    discriminator = Discriminator().to(DEVICE)

    # Loss function
    criterion = nn.BCELoss()

    # Optimizers
    optimizer_g = optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(BETA1, 0.999))
    optimizer_d = optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(BETA1, 0.999))

    # Fixed noise for tracking progress
    fixed_noise = torch.randn(16, LATENT_DIM, 1, 1, device=DEVICE)

    # Training loop
    g_losses = []
    d_losses = []

    print("Starting training...")
    print()

    for epoch in range(num_epochs):
        for i, (real_images, _) in enumerate(dataloader):
            batch_size = real_images.size(0)
            real_images = real_images.to(DEVICE)

            # Labels
            real_labels = torch.ones(batch_size, device=DEVICE)
            fake_labels = torch.zeros(batch_size, device=DEVICE)

            # ==================== Train Discriminator ====================
            discriminator.zero_grad()

            # Train on real images
            output_real = discriminator(real_images).view(-1)
            loss_d_real = criterion(output_real, real_labels)
            loss_d_real.backward()

            # Train on fake images
            noise = torch.randn(batch_size, LATENT_DIM, 1, 1, device=DEVICE)
            fake_images = generator(noise)
            output_fake = discriminator(fake_images.detach()).view(-1)
            loss_d_fake = criterion(output_fake, fake_labels)
            loss_d_fake.backward()

            # Update discriminator
            loss_d = loss_d_real + loss_d_fake
            optimizer_d.step()

            # ==================== Train Generator ====================
            generator.zero_grad()

            # Generator wants discriminator to think fakes are real
            output = discriminator(fake_images).view(-1)
            loss_g = criterion(output, real_labels)
            loss_g.backward()
            optimizer_g.step()

            # Record losses
            g_losses.append(loss_g.item())
            d_losses.append(loss_d.item())

        # Print progress
        print(f"Epoch [{epoch+1}/{num_epochs}] | "
              f"D Loss: {loss_d.item():.4f} | G Loss: {loss_g.item():.4f}")

        # Save sample images every 10 epochs
        if (epoch + 1) % 10 == 0 or epoch == 0:
            save_samples(generator, fixed_noise, epoch + 1)

    # Save final model
    torch.save(generator.state_dict(), 'generator_weights.pth')
    print(f"\nGenerator weights saved to generator_weights.pth")

    # Plot training losses
    plot_losses(g_losses, d_losses)

    return generator, discriminator


def save_samples(generator, noise, epoch):
    """Save generated samples to track training progress."""
    generator.eval()
    with torch.no_grad():
        fake = generator(noise).cpu()
    generator.train()

    # Convert to displayable format
    fake = (fake + 1) / 2  # [-1,1] -> [0,1]
    fake = fake.clamp(0, 1)

    # Create grid
    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i, ax in enumerate(axes.flat):
        img = fake[i].permute(1, 2, 0).numpy()
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle(f'Generated Samples - Epoch {epoch}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'samples_epoch_{epoch:03d}.png', dpi=100)
    plt.close()


def plot_losses(g_losses, d_losses):
    """Plot training loss curves."""
    plt.figure(figsize=(10, 5))
    plt.plot(g_losses, label='Generator Loss', alpha=0.7)
    plt.plot(d_losses, label='Discriminator Loss', alpha=0.7)
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.title('DCGAN Training Progress')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('training_losses.png', dpi=150)
    plt.close()
    print("Training loss plot saved to training_losses.png")


if __name__ == '__main__':
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at '{DATASET_PATH}'")
        print("Please run 'python create_dataset.py' first to generate the dataset.")
    else:
        train_dcgan()
