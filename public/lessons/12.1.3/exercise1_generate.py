import torch
from stylegan2_pytorch import Trainer
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# =============================================================================
# CONFIGURATION - Modify these values!
# =============================================================================

RANDOM_SEED = 42           # Try: 100, 777, 2024, or any number you like
TRUNCATION = 0.7           # Quality vs diversity (0.5 = safer, 1.0 = more diverse)
NUM_IMAGES = 16            # Number of patterns to generate (4x4 grid)

# =============================================================================
# Setup paths (don't modify)
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
MODELS_DIR = str(SCRIPT_DIR / 'models')
RESULTS_DIR = str(SCRIPT_DIR / 'training_results')
MODEL_NAME = 'african_fabrics'
IMAGE_SIZE = 64                # Must match training configuration

# =============================================================================
# Main script
# =============================================================================

def main():
    print("=" * 50)
    print("Exercise 1: Generate African Fabric Patterns")
    print("=" * 50)

    # Step 1: Check for GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    rank = 0 if device == 'cuda' else 'cpu'
    print(f"\nDevice: {device}")

    # Step 2: Load the trained model using Trainer
    print("\nLoading model...")
    try:
        trainer = Trainer(
            name=MODEL_NAME,
            results_dir=RESULTS_DIR,
            models_dir=MODELS_DIR,
            image_size=IMAGE_SIZE,
        )
        trainer.load(-1)  # Load latest checkpoint
        print("Model loaded!")
    except Exception as e:
        print(f"\nERROR: Could not load model.")
        print(f"Make sure you have trained a model (Exercise 3) or have")
        print(f"a pre-trained checkpoint in: {MODELS_DIR}")
        print(f"\nDetails: {e}")
        return

    # Step 3: Generate images with the chosen seed
    print(f"\nGenerating {NUM_IMAGES} patterns...")
    print(f"  Seed: {RANDOM_SEED}")
    print(f"  Truncation: {TRUNCATION}")

    torch.manual_seed(RANDOM_SEED)

    # Get the GAN model
    GAN = trainer.GAN
    GAN.eval()
    num_layers = GAN.GE.num_layers
    latent_dim = 512

    # Create image noise (same for all images)
    if device == 'cuda':
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.).cuda(rank)
    else:
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.)

    images = []
    with torch.no_grad():
        for i in range(NUM_IMAGES):
            # Generate random latent vector
            if device == 'cuda':
                latent = torch.randn(1, latent_dim).cuda(rank)
            else:
                latent = torch.randn(1, latent_dim)

            # Use the library's generate_truncated method
            latents = [(latent, num_layers)]
            generated = trainer.generate_truncated(GAN.SE, GAN.GE, latents, n, trunc_psi=TRUNCATION)

            # Convert to numpy
            img = generated[0].cpu().numpy()
            if img.shape[0] == 3:
                img = np.transpose(img, (1, 2, 0))

            # Already in [0, 1] range from generate_truncated
            img = np.clip(img, 0, 1)
            images.append(img)

    # Step 4: Create 4x4 grid visualization
    print("\nCreating visualization...")

    rows = int(np.sqrt(NUM_IMAGES))
    cols = (NUM_IMAGES + rows - 1) // rows

    fig, axes = plt.subplots(rows, cols, figsize=(12, 12))
    axes = axes.flatten()

    for i, (ax, img) in enumerate(zip(axes, images)):
        ax.imshow(img)
        ax.axis('off')

    # Hide empty subplots if any
    for i in range(len(images), len(axes)):
        axes[i].axis('off')

    plt.suptitle(f'Generated Patterns (Seed: {RANDOM_SEED}, Truncation: {TRUNCATION})',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    # Save with seed in filename
    output_file = f'generated_fabrics_seed{RANDOM_SEED}.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\nSaved: {output_file}")
    print("\n" + "=" * 50)
    print("What to do next:")
    print("=" * 50)
    print("1. Open the generated image and observe the patterns")
    print("2. Change RANDOM_SEED to 100 (or any other number)")
    print("3. Run the script again")
    print("4. Compare the two images - notice how different they are!")
    print("\nReflection: Each seed produces unique patterns, but they")
    print("all share the same 'African fabric' style learned by the model.")

if __name__ == '__main__':
    main()
