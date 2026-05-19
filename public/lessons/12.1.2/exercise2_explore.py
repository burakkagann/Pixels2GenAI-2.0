"""
Exercise 2: Explore Parameters

Experiment with DCGAN generation by modifying parameters and exploring
latent space interpolation.
"""

import torch
import matplotlib.pyplot as plt
import numpy as np
from dcgan_model import Generator, LATENT_DIM


def generate_grid(generator, num_rows=4, num_cols=4, seed=None):
    """Generate a grid of images."""
    if seed is not None:
        torch.manual_seed(seed)

    num_samples = num_rows * num_cols
    z = torch.randn(num_samples, LATENT_DIM, 1, 1)

    with torch.no_grad():
        images = generator(z)

    images = (images + 1) / 2
    images = images.clamp(0, 1)

    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 2.5, num_rows * 2.5))
    for i, ax in enumerate(axes.flat):
        if i < num_samples:
            img = images[i].permute(1, 2, 0).numpy()
            ax.imshow(img)
        ax.axis('off')

    return fig


def interpolate_latent(generator, num_steps=8, seed=42):
    """Create interpolation between two latent vectors."""
    torch.manual_seed(seed)
    z1 = torch.randn(LATENT_DIM)
    z2 = torch.randn(LATENT_DIM)

    fig, axes = plt.subplots(1, num_steps, figsize=(num_steps * 2, 2.5))

    generator.eval()
    with torch.no_grad():
        for i, ax in enumerate(axes):
            t = i / (num_steps - 1)
            z = (1 - t) * z1 + t * z2  # Linear interpolation
            z = z.view(1, LATENT_DIM, 1, 1)

            img = generator(z)
            img = (img + 1) / 2
            img = img.clamp(0, 1)
            img = img[0].permute(1, 2, 0).numpy()

            ax.imshow(img)
            ax.axis('off')
            ax.set_title(f't={t:.2f}', fontsize=9)

    plt.suptitle('Latent Space Interpolation', fontsize=12, fontweight='bold')
    plt.tight_layout()

    return fig


def main():
    """Explore DCGAN parameters."""
    print("=" * 60)
    print("Exercise 2: Explore Parameters")
    print("=" * 60)
    print()

    # Load pre-trained generator
    generator = Generator()
    generator.load_state_dict(torch.load('generator_weights.pth', map_location='cpu'))
    generator.eval()
    print("Generator loaded")
    print()

    # Goal 1: Generate larger grid (6x6)
    print("Goal 1: Generating 6x6 grid...")
    fig = generate_grid(generator, num_rows=6, num_cols=6, seed=123)
    plt.savefig('exercise2_grid_6x6.png', dpi=150, bbox_inches='tight')
    print("Saved to exercise2_grid_6x6.png")
    plt.close()

    # Goal 2: Explore interpolation
    print("Goal 2: Exploring latent space interpolation...")
    fig = interpolate_latent(generator, num_steps=8, seed=42)
    plt.savefig('exercise2_interpolation.png', dpi=150, bbox_inches='tight')
    print("Saved to exercise2_interpolation.png")
    plt.show()

    print()
    print("Try These Modifications:")
    print("1. Change seed values to generate different samples")
    print("2. Modify grid size (try 8x8 or 10x10)")
    print("3. Increase interpolation steps (try 16 or 32)")
    print("4. Compare different random seeds for interpolation")
    print()
    print("Exercise 2 complete!")


if __name__ == '__main__':
    main()
