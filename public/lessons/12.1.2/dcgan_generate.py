"""
Generate abstract art patterns using a pre-trained DCGAN.

This script loads a pre-trained Generator network and creates abstract art
by sampling from random latent vectors.

Based on PyTorch Official DCGAN Tutorial:
https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html
"""

import os
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image

from dcgan_model import Generator, LATENT_DIM


def generate_samples(generator, num_samples=16, seed=None):
    """
    Generate abstract art samples using the trained generator.

    Args:
        generator: Trained Generator model
        num_samples: Number of images to generate
        seed: Random seed for reproducibility (optional)

    Returns:
        numpy array of generated images
    """
    if seed is not None:
        torch.manual_seed(seed)
        np.random.seed(seed)

    # Create random latent vectors
    z = torch.randn(num_samples, LATENT_DIM, 1, 1)

    # Generate images
    generator.eval()
    with torch.no_grad():
        generated = generator(z)

    # Convert from [-1, 1] to [0, 1] for display
    generated = (generated + 1) / 2
    generated = generated.clamp(0, 1)

    # Convert to numpy (batch, channels, height, width) -> (batch, height, width, channels)
    images = generated.permute(0, 2, 3, 1).numpy()

    return images


def create_sample_grid(images, rows=4, cols=4):
    """
    Arrange generated images in a grid.

    Args:
        images: Array of images (num_samples, height, width, channels)
        rows: Number of rows in grid
        cols: Number of columns in grid

    Returns:
        Figure object
    """
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10))

    for i, ax in enumerate(axes.flat):
        if i < len(images):
            ax.imshow(images[i])
        ax.axis('off')

    plt.suptitle('DCGAN Generated Abstract Art\n(From Random Noise Vectors)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    return fig


def load_pretrained_generator(weights_path='generator_weights.pth'):
    """
    Load a pre-trained generator model.

    If weights file doesn't exist, creates a generator with random weights
    and provides a message about training.
    """
    generator = Generator()

    if os.path.exists(weights_path):
        generator.load_state_dict(torch.load(weights_path, map_location='cpu'))
        print(f"Loaded pre-trained weights from {weights_path}")
    else:
        print(f"Note: Pre-trained weights not found at {weights_path}")
        print("Using randomly initialized generator.")
        print("Run 'python dcgan_train.py' to train and save weights.")

    return generator


def main():
    """Main function to generate and display abstract art samples."""
    print("=" * 50)
    print("DCGAN Abstract Art Generator")
    print("=" * 50)

    # Load the generator
    generator = load_pretrained_generator()

    # Generate samples with a fixed seed for reproducibility
    print("\nGenerating 16 abstract art samples...")
    images = generate_samples(generator, num_samples=16, seed=42)

    # Create and save the grid
    fig = create_sample_grid(images)
    output_path = 'generated_samples.png'
    fig.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    print(f"Samples saved to {output_path}")

    # Also save individual samples
    print("\nSaving individual samples...")
    for i, img in enumerate(images[:4]):
        img_uint8 = (img * 255).astype(np.uint8)
        Image.fromarray(img_uint8).save(f'sample_{i+1}.png')

    print("Individual samples saved (sample_1.png through sample_4.png)")
    print("\nDone! Open generated_samples.png to view your AI art.")


if __name__ == '__main__':
    main()
