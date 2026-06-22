import os
import sys
from pathlib import Path

# Check for required library
try:
    from denoising_diffusion_pytorch import Unet, GaussianDiffusion
except ImportError:
    print("Error: denoising-diffusion-pytorch library not found.")
    print("Please install it with: pip install denoising-diffusion-pytorch")
    sys.exit(1)

import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Workshop utilities for device detection
from workshop_utils import get_device_with_confirmation

# =============================================================================
# Configuration
# =============================================================================

# Model parameters (must match training configuration)
IMAGE_SIZE = 64
BASE_CHANNELS = 64
CHANNEL_MULTS = (1, 2, 4, 8)
TIMESTEPS = 1000

# Model checkpoint path (prefers models/ but falls back to training_results/)
MODEL_PATH = 'models/ddpm_african_fabrics.pt'

def find_model_checkpoint():
    """Find the best available model checkpoint (EMA weights preferred)."""
    from pathlib import Path
    # First choice: consolidated model file
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    # Fallback: latest Trainer checkpoint (contains EMA weights)
    checkpoints = sorted(Path('training_results').glob('model-*.pt'))
    if checkpoints:
        print(f"Using Trainer checkpoint: {checkpoints[-1]}")
        return str(checkpoints[-1])
    return MODEL_PATH  # Will trigger "not found" warning in load_model

# Generation settings (NUM_SAMPLES set dynamically based on device)
SAMPLING_STEPS = 250     # Reduced steps using DDIM (faster)
RANDOM_SEED = 42         # For reproducible results

# =============================================================================
# Model Loading
# =============================================================================

def load_model(model_path, device='cpu'):
    """
    Load the trained DDPM model.

    Parameters:
        model_path: Path to saved model weights
        device: Device to load model on

    Returns:
        diffusion: GaussianDiffusion object with loaded weights
    """
    # Create model architecture
    model = Unet(
        dim=BASE_CHANNELS,
        dim_mults=CHANNEL_MULTS,
        flash_attn=False,
        channels=3
    )

    # Create diffusion process
    diffusion = GaussianDiffusion(
        model,
        image_size=IMAGE_SIZE,
        timesteps=TIMESTEPS,
        sampling_timesteps=SAMPLING_STEPS,
        objective='pred_noise'
    )

    # Load weights
    if os.path.exists(model_path):
        print(f"Loading model from: {model_path}")
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)

        # Handle trainer checkpoint format (contains EMA weights)
        if 'ema' in checkpoint:
            print("Loading EMA weights from trainer checkpoint...")
            ema_state = checkpoint['ema']
            state_dict = {}
            for key, value in ema_state.items():
                if key.startswith('ema_model.'):
                    new_key = key.replace('ema_model.', '')
                    state_dict[new_key] = value
            diffusion.load_state_dict(state_dict)
        else:
            # Simple state dict format
            model.load_state_dict(checkpoint)

        print("Model loaded successfully!")
    else:
        print(f"Warning: Model file not found at '{model_path}'")
        print("\nTo use this script, you need to either:")
        print("1. Complete Exercise 3 to train your own model")
        print("2. Download pre-trained weights from GitHub Releases:")
        print("   https://github.com/burakkagann/Pixels2GenAI/releases/tag/v1.0.0-ddpm-weights")
        print("\nUsing randomly initialized weights (output will be noise)")

    diffusion.to(device)
    diffusion.eval()

    return diffusion

# =============================================================================
# Image Generation
# =============================================================================

def generate_samples(diffusion, num_samples=16, seed=None, device='cpu'):
    """
    Generate fabric patterns using the trained model.

    Parameters:
        diffusion: Loaded GaussianDiffusion model
        num_samples: Number of images to generate
        seed: Random seed for reproducibility
        device: Device to generate on

    Returns:
        samples: Generated images as numpy array
    """
    if seed is not None:
        torch.manual_seed(seed)
        if device == 'cuda':
            torch.cuda.manual_seed(seed)

    print(f"\nGenerating {num_samples} samples...")
    print(f"Using {SAMPLING_STEPS} sampling steps (DDIM acceleration)")

    with torch.no_grad():
        samples = diffusion.sample(batch_size=num_samples)

    # Convert to numpy
    # Note: diffusion.sample() already returns [0, 1] (auto_normalize=True),
    # so we only need clamp as a safety net — no manual denormalization needed.
    samples = samples.cpu()
    samples = samples.clamp(0, 1)
    samples = samples.numpy()

    return samples

def create_grid(samples, grid_size=4):
    """
    Arrange samples into a grid image.

    Parameters:
        samples: Array of images [N, C, H, W]
        grid_size: Grid dimensions (grid_size x grid_size)

    Returns:
        grid: Single image containing all samples
    """
    n, c, h, w = samples.shape
    grid = np.zeros((c, h * grid_size, w * grid_size))

    for i in range(min(n, grid_size * grid_size)):
        row = i // grid_size
        col = i % grid_size
        grid[:, row*h:(row+1)*h, col*w:(col+1)*w] = samples[i]

    return grid.transpose(1, 2, 0)  # [C, H, W] -> [H, W, C]

def save_individual_samples(samples, output_dir='generated_samples'):
    """
    Save each generated sample as an individual image.

    Parameters:
        samples: Array of images [N, C, H, W]
        output_dir: Directory to save images
    """
    os.makedirs(output_dir, exist_ok=True)

    for i, sample in enumerate(samples):
        img = (sample.transpose(1, 2, 0) * 255).astype(np.uint8)
        img = Image.fromarray(img)
        img.save(os.path.join(output_dir, f'fabric_{i:04d}.png'))

    print(f"Saved {len(samples)} images to '{output_dir}/'")

# =============================================================================
# Main
# =============================================================================

def main():
    """Main generation function."""
    print("=" * 60)
    print("DDPM African Fabric Pattern Generator")
    print("=" * 60)

    # Device detection with user confirmation
    # Returns device and recommended sample count (GPU: 16, CPU: 4)
    device, num_samples = get_device_with_confirmation(task_type="generation")

    # Load model (auto-detects best available checkpoint)
    model_path = find_model_checkpoint()
    diffusion = load_model(model_path, device)

    # Generate samples
    samples = generate_samples(
        diffusion,
        num_samples=num_samples,
        seed=RANDOM_SEED,
        device=device
    )

    print(f"\nGenerated {len(samples)} fabric patterns")

    # Create and save grid
    grid_size = int(np.ceil(np.sqrt(num_samples)))
    grid = create_grid(samples, grid_size)

    plt.figure(figsize=(10, 10))
    plt.imshow(grid)
    plt.axis('off')
    plt.title('DDPM Generated African Fabric Patterns', fontsize=14)
    plt.tight_layout()
    plt.savefig('exercise1_output.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Saved grid to 'exercise1_output.png'")

    # Also save individual samples
    save_individual_samples(samples)

if __name__ == '__main__':
    main()
