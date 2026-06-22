import torch
from stylegan2_pytorch import Trainer
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
MODELS_DIR = str(SCRIPT_DIR / 'models')
RESULTS_DIR = str(SCRIPT_DIR / 'training_results')
MODEL_NAME = 'african_fabrics'
IMAGE_SIZE = 64  # Must match training configuration

# Generation parameters
NUM_IMAGES = 16  # Generate 4x4 grid
TRUNCATION = 0.7  # Quality-diversity balance (0.5-0.7 recommended)
RANDOM_SEED = 42  # For reproducible generation

# =============================================================================
# Helper Functions
# =============================================================================

def generate_image(trainer, GAN, latent, truncation, n, num_layers):
    """Generate a single image from latent vector with truncation."""
    with torch.no_grad():
        latents = [(latent, num_layers)]
        generated = trainer.generate_truncated(GAN.SE, GAN.GE, latents, n, trunc_psi=truncation)

        img = generated[0].cpu().numpy()
        if img.shape[0] == 3:
            img = np.transpose(img, (1, 2, 0))
        img = np.clip(img, 0, 1)
        return img

# =============================================================================
# Main Generation
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("StyleGAN2 Generation: African Fabric Patterns")
    print("=" * 60)

    # Check GPU availability
    print("\nStep 1: Checking device...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    rank = 0 if device == 'cuda' else 'cpu'
    print(f"  Using device: {device}")
    if device == 'cuda':
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    # Load model using Trainer
    print("\nStep 2: Loading model checkpoint...")
    try:
        trainer = Trainer(
            name=MODEL_NAME,
            results_dir=RESULTS_DIR,
            models_dir=MODELS_DIR,
            image_size=IMAGE_SIZE,
        )
        trainer.load(-1)  # Load latest checkpoint
        print("  Model loaded successfully!")
    except Exception as e:
        print(f"  ERROR loading model: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you ran exercise3_train.py or have the pre-trained checkpoint")
        print("2. Check that checkpoint file exists in ./models/")
        print("3. Verify the checkpoint is not corrupted")
        exit(1)

    # Get the GAN model
    GAN = trainer.GAN
    GAN.eval()

    # Get number of layers
    num_layers = GAN.GE.num_layers

    # Create image noise
    if device == 'cuda':
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.).cuda(rank)
    else:
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.)

    # Generate 4x4 grid of images
    print("\nStep 3: Generating images...")
    print(f"  Number of images: {NUM_IMAGES}")
    print(f"  Truncation (psi): {TRUNCATION}")
    print(f"  Random seed: {RANDOM_SEED}")

    torch.manual_seed(RANDOM_SEED)

    print("  Generating (this may take a minute)...")
    images = []
    for i in range(NUM_IMAGES):
        if device == 'cuda':
            latent = torch.randn(1, 512).cuda(rank)
        else:
            latent = torch.randn(1, 512)

        img = generate_image(trainer, GAN, latent, TRUNCATION, n, num_layers)
        images.append(img)

    # Create 4x4 grid visualization
    print("\nStep 4: Creating visualization...")
    fig, axes = plt.subplots(4, 4, figsize=(12, 12))
    axes = axes.flatten()

    for i, (ax, img) in enumerate(zip(axes, images)):
        ax.imshow(img)
        ax.axis('off')
        ax.set_title(f'Sample {i+1}', fontsize=9)

    plt.suptitle(f'Generated African Fabric Patterns (Truncation = {TRUNCATION})',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('generated_fabrics.png', dpi=150, bbox_inches='tight')
    print("  Saved: generated_fabrics.png")

    # Generate latent space interpolation
    print("\nStep 5: Generating interpolation between two patterns...")
    torch.manual_seed(100)
    if device == 'cuda':
        latent_a = torch.randn(1, 512).cuda(rank)
    else:
        latent_a = torch.randn(1, 512)

    torch.manual_seed(200)
    if device == 'cuda':
        latent_b = torch.randn(1, 512).cuda(rank)
    else:
        latent_b = torch.randn(1, 512)

    # Create 10 interpolation steps
    steps = 10
    alphas = np.linspace(0, 1, steps)

    print(f"  Generating {steps} interpolation steps...")
    interpolated_images = []
    for alpha in alphas:
        latent = (1 - alpha) * latent_a + alpha * latent_b
        img = generate_image(trainer, GAN, latent, TRUNCATION, n, num_layers)
        interpolated_images.append(img)

    # Create horizontal strip
    fig, axes = plt.subplots(1, 10, figsize=(20, 2))
    for i, (ax, img) in enumerate(zip(axes, interpolated_images)):
        ax.imshow(img)
        ax.axis('off')

    plt.suptitle('Latent Space Interpolation (Smooth Morphing Between Two Patterns)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('fabric_interpolation.png', dpi=150, bbox_inches='tight')
    print("  Saved: fabric_interpolation.png")

    # Final summary
    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. generated_fabrics.png - 4x4 grid of novel fabric patterns")
    print("  2. fabric_interpolation.png - Smooth morphing between two patterns")
    print("\nExperiment ideas:")
    print("  - Change TRUNCATION to 0.5 (higher quality) or 1.0 (more diversity)")
    print("  - Modify NUM_IMAGES to generate more or fewer samples")
    print("  - Change RANDOM_SEED to generate different patterns")
    print("  - Explore style mixing by modifying the script")
