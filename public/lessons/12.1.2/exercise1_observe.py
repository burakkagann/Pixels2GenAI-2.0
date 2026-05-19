"""
Exercise 1: Observe DCGAN Generation

Load a pre-trained generator and observe how it creates abstract art
from random noise vectors.
"""

import torch
import matplotlib.pyplot as plt
from dcgan_model import Generator, LATENT_DIM


def main():
    """Generate and display abstract art samples."""
    print("=" * 60)
    print("Exercise 1: Observe DCGAN Generation")
    print("=" * 60)
    print()

    # Load pre-trained generator
    generator = Generator()
    generator.load_state_dict(torch.load('generator_weights.pth', map_location='cpu'))
    generator.eval()
    print("Pre-trained generator loaded")
    print()

    # Print model information
    total_params = sum(p.numel() for p in generator.parameters())
    print(f"Generator Architecture:")
    print(f"  Input: {LATENT_DIM}-dimensional latent vector")
    print(f"  Output: 64x64 RGB image")
    print(f"  Total parameters: {total_params:,}")
    print()

    # Generate 16 samples
    print("Generating 16 abstract art samples...")
    torch.manual_seed(42)  # For reproducibility
    z = torch.randn(16, LATENT_DIM, 1, 1)

    with torch.no_grad():
        images = generator(z)

    # Convert from [-1, 1] to [0, 1]
    images = (images + 1) / 2
    images = images.clamp(0, 1)

    # Display in 4x4 grid
    fig, axes = plt.subplots(4, 4, figsize=(10, 10))
    for i, ax in enumerate(axes.flat):
        img = images[i].permute(1, 2, 0).numpy()
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle('DCGAN Generated Abstract Art (4x4 Grid)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('exercise1_output.png', dpi=150, bbox_inches='tight')
    print("Saved output to exercise1_output.png")
    plt.show()

    print()
    print("Reflection Questions:")
    print("1. How does the latent vector size (100 dimensions) affect generation?")
    print("2. What common visual patterns do you observe across samples?")
    print("3. Why does the generator use Tanh activation in the output layer?")
    print()
    print("Exercise 1 complete!")


if __name__ == '__main__':
    main()
