"""
Exercise 3: Train on African Fabric Patterns

Train a DCGAN from scratch on African fabric patterns from Kaggle.
This is a simplified version of dcgan_train.py for educational purposes.
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
import matplotlib.pyplot as plt
from glob import glob
from PIL import Image as PILImage

from dcgan_model import Generator, Discriminator, LATENT_DIM


# Training configuration
DATASET_PATH = 'african_fabric_processed'
BATCH_SIZE = 64
NUM_EPOCHS = 100  # Extended from 50 to 100 epochs
LEARNING_RATE = 0.0002
IMG_SIZE = 64

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class AfricanFabricDataset(torch.utils.data.Dataset):
    """Dataset loader for African fabric pattern images."""

    def __init__(self, folder_path, transform=None):
        self.image_paths = sorted(glob(os.path.join(folder_path, '*.png')))
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img = PILImage.open(self.image_paths[idx]).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img


def train():
    """Train the DCGAN."""
    print("=" * 60)
    print("Exercise 3: Train DCGAN on African Fabric Patterns")
    print("=" * 60)
    print(f"Device: {DEVICE}")
    print(f"Epochs: {NUM_EPOCHS}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    # Setup dataset
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])

    dataset = AfricanFabricDataset(DATASET_PATH, transform=transform)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    print(f"Dataset: {len(dataset)} African fabric images")
    print(f"Batches per epoch: {len(dataloader)}")
    print()

    # Initialize models
    generator = Generator().to(DEVICE)
    discriminator = Discriminator().to(DEVICE)

    # Loss and optimizers
    criterion = nn.BCELoss()
    optimizer_g = optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))
    optimizer_d = optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))

    # Fixed noise for tracking progress
    fixed_noise = torch.randn(16, LATENT_DIM, 1, 1, device=DEVICE)

    # Training tracking
    g_losses = []
    d_losses = []

    print("Starting training...")
    print()

    # Training loop
    for epoch in range(NUM_EPOCHS):
        for i, real_images in enumerate(dataloader):
            batch_size = real_images.size(0)
            real_images = real_images.to(DEVICE)

            real_labels = torch.ones(batch_size, device=DEVICE)
            fake_labels = torch.zeros(batch_size, device=DEVICE)

            # Train Discriminator
            discriminator.zero_grad()

            output_real = discriminator(real_images).view(-1)
            loss_d_real = criterion(output_real, real_labels)
            loss_d_real.backward()

            noise = torch.randn(batch_size, LATENT_DIM, 1, 1, device=DEVICE)
            fake_images = generator(noise)
            output_fake = discriminator(fake_images.detach()).view(-1)
            loss_d_fake = criterion(output_fake, fake_labels)
            loss_d_fake.backward()

            loss_d = loss_d_real + loss_d_fake
            optimizer_d.step()

            # Train Generator
            generator.zero_grad()
            output = discriminator(fake_images).view(-1)
            loss_g = criterion(output, real_labels)
            loss_g.backward()
            optimizer_g.step()

            # Record losses
            g_losses.append(loss_g.item())
            d_losses.append(loss_d.item())

        # Print progress
        print(f"Epoch [{epoch+1}/{NUM_EPOCHS}] | D Loss: {loss_d.item():.4f} | G Loss: {loss_g.item():.4f}")

        # Save samples at key epochs
        if epoch + 1 in [10, 30, 50, 70, 100]:
            save_progress(generator, fixed_noise, epoch + 1)

    # Save final model
    torch.save(generator.state_dict(), 'exercise3_generator.pth')
    print("\nGenerator saved to exercise3_generator.pth")

    # Plot training losses
    plot_training_progress(g_losses, d_losses)

    # Generate final samples
    generate_final_samples(generator)

    print("\nTraining complete!")


def save_progress(generator, noise, epoch):
    """Save generated samples at checkpoints."""
    generator.eval()
    with torch.no_grad():
        fake = generator(noise).cpu()
    generator.train()

    fake = (fake + 1) / 2
    fake = fake.clamp(0, 1)

    fig, axes = plt.subplots(4, 4, figsize=(8, 8))
    for i, ax in enumerate(axes.flat):
        img = fake[i].permute(1, 2, 0).numpy()
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle(f'Generated Samples - Epoch {epoch}', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'exercise3_epoch_{epoch}.png', dpi=100)
    plt.close()
    print(f"  Saved exercise3_epoch_{epoch}.png")


def plot_training_progress(g_losses, d_losses):
    """Plot and save training loss curves."""
    plt.figure(figsize=(10, 5))
    plt.plot(g_losses, label='Generator Loss', alpha=0.7, color='blue')
    plt.plot(d_losses, label='Discriminator Loss', alpha=0.7, color='red')
    plt.xlabel('Training Steps')
    plt.ylabel('Loss')
    plt.title('DCGAN Training Progress')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('exercise3_training_progress.png', dpi=150)
    plt.close()
    print("Saved exercise3_training_progress.png")


def generate_final_samples(generator):
    """Generate final sample grid."""
    generator.eval()
    noise = torch.randn(16, LATENT_DIM, 1, 1, device=DEVICE)

    with torch.no_grad():
        images = generator(noise).cpu()

    images = (images + 1) / 2
    images = images.clamp(0, 1)

    fig, axes = plt.subplots(4, 4, figsize=(10, 10))
    for i, ax in enumerate(axes.flat):
        img = images[i].permute(1, 2, 0).numpy()
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle('Final Generated Samples (After 100 Epochs)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('exercise3_final_samples.png', dpi=150)
    plt.close()
    print("Saved exercise3_final_samples.png")


if __name__ == '__main__':
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset directory '{DATASET_PATH}' not found!")
        print("Please complete the dataset setup steps:")
        print("1. Download the African fabric dataset from Kaggle:")
        print("   https://www.kaggle.com/datasets/mikuns/african-fabric")
        print("2. Extract to 'african_fabric_dataset/' directory")
        print("3. Run 'python preprocess_african_fabric.py' to prepare the dataset")
        print("\nSee README.rst for detailed instructions.")
    else:
        # Check if dataset has images
        from pathlib import Path
        image_files = list(Path(DATASET_PATH).glob('*.png'))
        if len(image_files) == 0:
            print(f"Error: No images found in '{DATASET_PATH}'!")
            print("Please ensure you've downloaded and preprocessed the African fabric dataset.")
            print("Run 'python preprocess_african_fabric.py' to prepare the dataset.")
        else:
            train()
