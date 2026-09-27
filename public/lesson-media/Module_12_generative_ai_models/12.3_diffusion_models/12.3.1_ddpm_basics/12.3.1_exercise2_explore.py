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

# Optional: imageio for GIF creation
try:
    import imageio.v2 as imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    print("Note: imageio not installed. GIF creation will be skipped.")
    print("Install with: pip install imageio")

# =============================================================================
# CONFIG -- Change these values for Exercise 2 goals (see README for details)
# =============================================================================

# Goal 1: DDIM sampling speed (try 50, 250, 1000)
SAMPLING_STEPS = 250

# Goal 2: Forward diffusion timesteps to visualize (add early values like 25, 50)
TIMESTEPS_TO_SHOW = [0, 100, 250, 500, 750, 999]

# Goal 3: Random seed controls pattern identity (try 7, 42, 123, 999)
RANDOM_SEED = 42

# Goal 4: Denoising capture points (add values like 900, 700, 500, 300)
CAPTURE_TIMESTEPS = [999, 800, 600, 400, 200, 100, 50, 0]

# =============================================================================
# Model parameters (do not change -- must match training)
# =============================================================================
IMAGE_SIZE = 64
BASE_CHANNELS = 64
CHANNEL_MULTS = (1, 2, 4, 8)
TIMESTEPS = 1000
MODEL_PATH = 'models/ddpm_african_fabrics.pt'

def find_model_checkpoint():
    """Find the best available model checkpoint (EMA weights preferred)."""
    from pathlib import Path
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    checkpoints = sorted(Path('training_results').glob('model-*.pt'))
    if checkpoints:
        print(f"Using Trainer checkpoint: {checkpoints[-1]}")
        return str(checkpoints[-1])
    return MODEL_PATH

# =============================================================================
# Model Loading
# =============================================================================

def load_model(model_path, sampling_steps=250, device='cpu'):
    """Load the trained DDPM model with configurable sampling steps."""
    model = Unet(
        dim=BASE_CHANNELS,
        dim_mults=CHANNEL_MULTS,
        flash_attn=False,
        channels=3
    )

    diffusion = GaussianDiffusion(
        model,
        image_size=IMAGE_SIZE,
        timesteps=TIMESTEPS,
        sampling_timesteps=sampling_steps,
        objective='pred_noise'
    )

    if os.path.exists(model_path):
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)

        # Handle trainer checkpoint format (contains EMA weights)
        if 'ema' in checkpoint:
            ema_state = checkpoint['ema']
            state_dict = {k.replace('ema_model.', ''): v
                         for k, v in ema_state.items() if k.startswith('ema_model.')}
            diffusion.load_state_dict(state_dict)
        else:
            model.load_state_dict(checkpoint)
    else:
        print(f"Warning: Model not found at '{model_path}'")
        print("Download from: https://github.com/burakkagann/Pixels2GenAI/releases/tag/v1.0.0-ddpm-weights")
        print("Using random weights (output will be noise)")

    diffusion.to(device)
    diffusion.eval()

    return diffusion

# =============================================================================
# Exploration 1: Sampling Steps Comparison
# =============================================================================

def compare_sampling_steps(device='cpu'):
    """
    Compare generation quality at different sampling step counts.

    Fewer steps = faster generation but potentially lower quality.
    More steps = slower generation but potentially higher quality.
    DDIM allows using fewer steps while maintaining reasonable quality.
    """
    print("\n" + "=" * 60)
    print("Exploration 1: Sampling Steps Comparison")
    print("=" * 60)

    step_counts = [50, 100, 250, 500, 1000]
    torch.manual_seed(RANDOM_SEED)

    # Use same starting noise for fair comparison
    starting_noise = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)

    results = []

    for steps in step_counts:
        print(f"\nGenerating with {steps} sampling steps...")

        # Create model with specific sampling steps
        model = Unet(dim=BASE_CHANNELS, dim_mults=CHANNEL_MULTS, flash_attn=False, channels=3)
        diffusion = GaussianDiffusion(
            model,
            image_size=IMAGE_SIZE,
            timesteps=TIMESTEPS,
            sampling_timesteps=steps,
            objective='pred_noise'
        )

        model_path = find_model_checkpoint()
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=device, weights_only=False)
            if 'ema' in checkpoint:
                ema_state = checkpoint['ema']
                state_dict = {k.replace('ema_model.', ''): v
                             for k, v in ema_state.items() if k.startswith('ema_model.')}
                diffusion.load_state_dict(state_dict)
            else:
                model.load_state_dict(checkpoint)

        diffusion.to(device)
        diffusion.eval()

        # Generate sample
        with torch.no_grad():
            sample = diffusion.sample(batch_size=1)

        # Convert to numpy
        # diffusion.sample() already returns [0, 1] (auto_normalize=True)
        sample = sample.cpu()
        sample = sample.clamp(0, 1)[0].permute(1, 2, 0).numpy()

        results.append((steps, sample))

    # Create comparison figure
    fig, axes = plt.subplots(1, len(step_counts), figsize=(15, 3))

    for i, (steps, img) in enumerate(results):
        axes[i].imshow(img)
        axes[i].set_title(f'{steps} steps', fontsize=10)
        axes[i].axis('off')

    plt.suptitle('Effect of Sampling Steps on Generation Quality', fontsize=12)
    plt.tight_layout()
    plt.savefig('exercise2_sampling_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\nSaved comparison to 'exercise2_sampling_comparison.png'")
    print("\nObservations:")
    print("- Fewer steps (50-100): Faster but may show artifacts")
    print("- Medium steps (250): Good balance of quality and speed")
    print("- Many steps (500-1000): Best quality but slower")

# =============================================================================
# Exploration 2: Denoising Visualization
# =============================================================================

def visualize_denoising_process(device='cpu'):
    """
    Visualize the step-by-step denoising process.

    Shows how pure noise gradually transforms into a coherent image
    through the reverse diffusion process.
    """
    print("\n" + "=" * 60)
    print("Exploration 2: Denoising Process Visualization")
    print("=" * 60)

    # Load model
    model_path = find_model_checkpoint()
    diffusion = load_model(model_path, sampling_steps=1000, device=device)

    torch.manual_seed(RANDOM_SEED)

    # We'll manually step through the sampling process to capture intermediates
    print("\nGenerating with full 1000 steps to capture intermediates...")

    # Start from pure noise
    x = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)

    # Capture images at specific timesteps (configured in CONFIG section)
    capture_timesteps = CAPTURE_TIMESTEPS
    captured_images = []

    # Get the model's internal step sequence
    timesteps_seq = list(reversed(range(TIMESTEPS)))

    with torch.no_grad():
        for i, t in enumerate(timesteps_seq):
            t_batch = torch.full((1,), t, device=device, dtype=torch.long)

            # One denoising step using internal method
            # Note: This is a simplified version - actual DDIM uses different math
            betas = diffusion.betas[t]
            alphas = 1 - betas
            alphas_cumprod = diffusion.alphas_cumprod[t]

            # Predict noise
            pred_noise = diffusion.model(x, t_batch)

            # Compute predicted x0 and next x
            sqrt_alphas_cumprod = torch.sqrt(alphas_cumprod)
            sqrt_one_minus_alphas_cumprod = torch.sqrt(1 - alphas_cumprod)

            # Predicted clean image
            pred_x0 = (x - sqrt_one_minus_alphas_cumprod * pred_noise) / sqrt_alphas_cumprod

            if t in capture_timesteps:
                img = x.cpu()[0]
                img = (img + 1) / 2
                img = img.clamp(0, 1).permute(1, 2, 0).numpy()
                captured_images.append((t, img.copy()))

            # Next step (simplified DDPM update)
            if t > 0:
                noise = torch.randn_like(x) if t > 1 else 0
                posterior_var = betas * (1 - diffusion.alphas_cumprod_prev[t]) / (1 - alphas_cumprod)
                x = (1 / torch.sqrt(alphas)) * (x - betas * pred_noise / sqrt_one_minus_alphas_cumprod)
                x = x + torch.sqrt(posterior_var) * noise

    # Create figure showing denoising progression
    fig, axes = plt.subplots(1, len(captured_images), figsize=(16, 2.5))

    for i, (t, img) in enumerate(captured_images):
        axes[i].imshow(img)
        axes[i].set_title(f't={t}', fontsize=9)
        axes[i].axis('off')

    plt.suptitle('Reverse Diffusion: From Noise to Image', fontsize=12)
    plt.tight_layout()
    plt.savefig('reverse_diffusion_demo.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Saved denoising steps to 'reverse_diffusion_demo.png'")

    # Create animated GIF if imageio is available
    if IMAGEIO_AVAILABLE and len(captured_images) > 0:
        print("\nCreating denoising animation...")
        frames = []

        # Add more intermediate frames for smooth animation
        for t, img in reversed(captured_images):
            frame = (img * 255).astype(np.uint8)
            # Hold each frame for multiple times
            for _ in range(5):
                frames.append(frame)

        imageio.mimsave('exercise2_denoising.gif', frames, fps=10, loop=0)
        print("Saved animation to 'exercise2_denoising.gif'")

# =============================================================================
# Exploration 3: Forward Diffusion (Adding Noise)
# =============================================================================

def visualize_forward_diffusion(device='cpu'):
    """
    Visualize the forward diffusion process (adding noise).

    Shows how a clean image is progressively corrupted with noise
    over multiple timesteps. This is what the model learns to reverse.
    """
    print("\n" + "=" * 60)
    print("Exploration 3: Forward Diffusion (Adding Noise)")
    print("=" * 60)

    # Load a sample image from training data
    dataset_path = '../../12.1_generative_adversarial_networks/12.1.2_dcgan_art/african_fabric_processed'

    if not os.path.exists(dataset_path):
        print("Training dataset not found. Using generated noise instead.")
        x_0 = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    else:
        # Load first image
        img_path = sorted(Path(dataset_path).glob('*.png'))[0]
        img = Image.open(img_path).convert('RGB')
        img = np.array(img) / 255.0
        img = (img - 0.5) / 0.5  # Normalize to [-1, 1]
        x_0 = torch.FloatTensor(img).permute(2, 0, 1).unsqueeze(0)

    # Create diffusion process for forward sampling
    model = Unet(dim=BASE_CHANNELS, dim_mults=CHANNEL_MULTS, flash_attn=False, channels=3)
    diffusion = GaussianDiffusion(model, image_size=IMAGE_SIZE, timesteps=TIMESTEPS)

    # Visualize at different timesteps (configured in CONFIG section)
    timesteps = TIMESTEPS_TO_SHOW
    noisy_images = []

    for t in timesteps:
        t_tensor = torch.tensor([t])
        noise = torch.randn_like(x_0)

        # Apply forward diffusion
        sqrt_alphas_cumprod = diffusion.sqrt_alphas_cumprod[t]
        sqrt_one_minus = torch.sqrt(1 - diffusion.alphas_cumprod[t])

        x_t = sqrt_alphas_cumprod * x_0 + sqrt_one_minus * noise

        # Convert to displayable image
        img = x_t[0].permute(1, 2, 0).numpy()
        img = (img + 1) / 2  # Denormalize
        img = np.clip(img, 0, 1)

        noisy_images.append((t, img))

    # Create figure
    fig, axes = plt.subplots(1, len(timesteps), figsize=(15, 3))

    for i, (t, img) in enumerate(noisy_images):
        axes[i].imshow(img)
        axes[i].set_title(f't={t}', fontsize=10)
        axes[i].axis('off')

    plt.suptitle('Forward Diffusion: Gradually Adding Noise', fontsize=12)
    plt.tight_layout()
    plt.savefig('forward_diffusion_demo.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Saved forward diffusion demo to 'forward_diffusion_demo.png'")
    print("\nObservations:")
    print("- t=0: Original clean image")
    print("- t=100-250: Some noise, structure still visible")
    print("- t=500-750: Heavily corrupted, patterns fading")
    print("- t=999: Almost pure noise, original unrecognizable")

# =============================================================================
# Main
# =============================================================================

def main():
    """Run explorations (all by default, or a single goal with --goal N)."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Explore DDPM diffusion parameters')
    parser.add_argument(
        '--goal', type=int, choices=[1, 2, 3, 4], default=None,
        help='Run a single goal (1=sampling steps, 2=forward diffusion, '
             '3=seed identity, 4=denoising detail). Omit to run all.')
    args = parser.parse_args()

    print("=" * 60)
    print("DDPM Parameter Exploration")
    print("=" * 60)

    # Device detection with user confirmation
    device, _ = get_device_with_confirmation(task_type="exploration")

    run_all = args.goal is None

    # Goal 1 & 3 both use compare_sampling_steps (SAMPLING_STEPS and RANDOM_SEED)
    if run_all or args.goal in (1, 3):
        print("\n" + "~" * 60)
        compare_sampling_steps(device)

    # Goal 2 uses visualize_forward_diffusion (TIMESTEPS_TO_SHOW)
    if run_all or args.goal == 2:
        print("\n" + "~" * 60)
        visualize_forward_diffusion(device)

    # Goal 4 uses visualize_denoising_process (CAPTURE_TIMESTEPS)
    if run_all or args.goal == 4:
        print("\n" + "~" * 60)
        visualize_denoising_process(device)

    # Summary
    print("\n" + "=" * 60)
    print("Exploration Complete")
    print("=" * 60)
    if run_all:
        print("""
Generated files:
- forward_diffusion_demo.png: How noise is added during training
- exercise2_sampling_comparison.png: Quality vs speed trade-off
- reverse_diffusion_demo.png: Step-by-step reverse process
- exercise2_denoising.gif: Animated denoising (if imageio installed)
        """)
    print("Tip: use --goal N to run a single exploration faster.")
    print("See the README for Goals 1-4: change values in the CONFIG section")
    print("at the top of this script, then re-run to observe the effects.")

if __name__ == '__main__':
    main()
