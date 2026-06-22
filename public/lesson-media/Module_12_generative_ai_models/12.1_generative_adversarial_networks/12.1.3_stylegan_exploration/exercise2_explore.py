import torch
from stylegan2_pytorch import Trainer
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Optional: imageio for GIF creation
try:
    import imageio.v2 as imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    print("Note: imageio not installed. GIF creation will be skipped.")
    print("Install with: pip install imageio")

# =============================================================================
# CONFIGURATION - Modify these values!
# =============================================================================

# For truncation comparison
TRUNCATION_VALUES = [0.3, 0.5, 0.7, 1.0]  # Different psi values to compare
COMPARISON_SEED = 42                        # Same seed for fair comparison

# For morphing animation
SEED_A = 42       # Starting pattern
SEED_B = 100      # Ending pattern
NUM_FRAMES = 30   # Frames in the morphing animation
FPS = 10          # Frames per second for GIF

# =============================================================================
# Setup paths (don't modify)
# =============================================================================

SCRIPT_DIR = Path(__file__).parent.resolve()
MODELS_DIR = str(SCRIPT_DIR / 'models')
RESULTS_DIR = str(SCRIPT_DIR / 'training_results')
MODEL_NAME = 'african_fabrics'
IMAGE_SIZE = 64                # Must match training configuration

# =============================================================================
# Helper function for generation
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
# Part A: Truncation Comparison
# =============================================================================

def compare_truncation(trainer, GAN, device, rank, num_layers):
    """Generate images at different truncation values for comparison."""
    print("\n" + "=" * 50)
    print("Part A: Truncation Comparison")
    print("=" * 50)

    # Generate same 4 images at each truncation level
    num_samples = 4
    fig, axes = plt.subplots(len(TRUNCATION_VALUES), num_samples,
                              figsize=(12, 3 * len(TRUNCATION_VALUES)))

    # Create image noise
    if device == 'cuda':
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.).cuda(rank)
    else:
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.)

    for row, psi in enumerate(TRUNCATION_VALUES):
        print(f"  Generating with truncation = {psi}...")

        # Use same seed for fair comparison
        torch.manual_seed(COMPARISON_SEED)

        for col in range(num_samples):
            if device == 'cuda':
                latent = torch.randn(1, 512).cuda(rank)
            else:
                latent = torch.randn(1, 512)

            img = generate_image(trainer, GAN, latent, psi, n, num_layers)

            ax = axes[row, col]
            ax.imshow(img)
            ax.axis('off')

            # Add row labels
            if col == 0:
                ax.set_ylabel(f'psi = {psi}', fontsize=12, fontweight='bold')

    # Add column labels
    for col in range(num_samples):
        axes[0, col].set_title(f'Sample {col + 1}', fontsize=10)

    plt.suptitle('Truncation Trick: Quality vs Diversity Trade-off\n'
                 'Lower psi = More similar (safer) | Higher psi = More diverse (riskier)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('truncation_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\nSaved: truncation_comparison.png")
    print("\nWhat to observe:")
    print("  - psi = 0.3: Patterns look very similar (safe but boring)")
    print("  - psi = 0.7: Good balance of quality and variety")
    print("  - psi = 1.0: Maximum diversity but some may look odd")

# =============================================================================
# Part B: Morphing Animation
# =============================================================================

def create_morphing_gif(trainer, GAN, device, rank, num_layers):
    """Create an animated GIF morphing between two patterns."""
    print("\n" + "=" * 50)
    print("Part B: Morphing Animation")
    print("=" * 50)

    if not IMAGEIO_AVAILABLE:
        print("Skipping GIF creation (imageio not installed)")
        return

    # Generate two latent vectors
    print(f"  Pattern A: seed {SEED_A}")
    print(f"  Pattern B: seed {SEED_B}")
    print(f"  Frames: {NUM_FRAMES}")

    torch.manual_seed(SEED_A)
    if device == 'cuda':
        latent_a = torch.randn(1, 512).cuda(rank)
    else:
        latent_a = torch.randn(1, 512)

    torch.manual_seed(SEED_B)
    if device == 'cuda':
        latent_b = torch.randn(1, 512).cuda(rank)
    else:
        latent_b = torch.randn(1, 512)

    # Create image noise
    if device == 'cuda':
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.).cuda(rank)
    else:
        n = torch.FloatTensor(1, IMAGE_SIZE, IMAGE_SIZE, 1).uniform_(0., 1.)

    # Generate interpolated frames
    print("  Generating frames...")
    frames = []
    alphas = np.linspace(0, 1, NUM_FRAMES)

    for i, alpha in enumerate(alphas):
        # Linear interpolation in latent space
        latent = (1 - alpha) * latent_a + alpha * latent_b
        img = generate_image(trainer, GAN, latent, 0.7, n, num_layers)

        # Convert to uint8 for imageio
        frame = (img * 255).astype(np.uint8)
        frames.append(frame)

        if (i + 1) % 10 == 0:
            print(f"    Frame {i + 1}/{NUM_FRAMES}")

    # Save as GIF
    print("  Creating GIF...")
    imageio.mimsave('fabric_morph.gif', frames, fps=FPS, loop=0)
    print("\nSaved: fabric_morph.gif")

    # Also save start and end frames as static images
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(frames[0])
    plt.title(f'Start (Seed {SEED_A})', fontsize=12, fontweight='bold')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(frames[-1])
    plt.title(f'End (Seed {SEED_B})', fontsize=12, fontweight='bold')
    plt.axis('off')

    plt.suptitle('Morphing Endpoints', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('morph_endpoints.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Saved: morph_endpoints.png")
    print("\nWhat to observe:")
    print("  - The morph is smooth because latent space is continuous")
    print("  - Intermediate frames are valid fabric patterns (not glitchy)")
    print("  - This demonstrates how StyleGAN 'understands' the fabric domain")

# =============================================================================
# Main script
# =============================================================================

def main():
    print("=" * 50)
    print("Exercise 2: Explore StyleGAN2 Parameters")
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

    # Get the GAN model
    GAN = trainer.GAN
    GAN.eval()
    num_layers = GAN.GE.num_layers

    # Part A: Truncation comparison
    compare_truncation(trainer, GAN, device, rank, num_layers)

    # Part B: Morphing animation
    create_morphing_gif(trainer, GAN, device, rank, num_layers)

    # Summary
    print("\n" + "=" * 50)
    print("Exercise 2 Complete!")
    print("=" * 50)
    print("\nGenerated files:")
    print("  1. truncation_comparison.png - Different psi values compared")
    if IMAGEIO_AVAILABLE:
        print("  2. fabric_morph.gif - Animated morphing between patterns")
        print("  3. morph_endpoints.png - Start and end patterns")

    print("\nReflection questions:")
    print("  1. Which truncation value produces the most pleasing results?")
    print("  2. Why does the morphing animation look smooth and natural?")
    print("  3. What would happen if you morphed between very different seeds?")

if __name__ == '__main__':
    main()
