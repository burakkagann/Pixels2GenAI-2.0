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
from PIL import Image
from tqdm import tqdm

try:
    import imageio.v2 as imageio
except ImportError:
    import imageio

# =============================================================================
# Configuration
# =============================================================================

# Model checkpoint path (auto-detects latest, uses EMA weights for best quality)
MODEL_PATH = 'models/ddpm_african_fabrics.pt'

def find_latest_checkpoint():
    """Find the best available model checkpoint."""
    # First choice: consolidated model file (contains EMA weights after training fix)
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    # Fallback: latest Trainer checkpoint
    checkpoints = sorted(Path('training_results').glob('model-*.pt'))
    if checkpoints:
        return str(checkpoints[-1])
    return MODEL_PATH

# Model architecture (must match training configuration)
IMAGE_SIZE = 64
BASE_CHANNELS = 64
CHANNEL_MULTS = (1, 2, 4, 8)
TIMESTEPS = 1000

# Animation parameters
NUM_KEYFRAMES = 4           # Number of distinct patterns to morph between
DURATION_SECONDS = 8        # Total animation duration (shorter for manageable file size)
FPS = 12                    # Frames per second (GIF-appropriate rate)
OUTPUT_SIZE = 256           # Output resolution (upscaled from 64x64)

# Sampling parameters
SAMPLING_STEPS = 250        # DDIM steps (matches training config for best quality)
RANDOM_SEED = 123           # For reproducible keyframes (change for different patterns)

# Output file
OUTPUT_PATH = os.path.join('visuals', 'ddpm_fabric_morph.gif')

# =============================================================================
# SLERP Interpolation
# =============================================================================

def slerp(val, low, high):
    """
    Spherical linear interpolation between two tensors.

    SLERP produces smoother interpolations than linear interpolation
    for high-dimensional vectors like noise, as it interpolates along
    the surface of a hypersphere rather than cutting through it.

    Parameters:
        val: Interpolation factor (0.0 = low, 1.0 = high)
        low: Starting tensor
        high: Ending tensor

    Returns:
        Interpolated tensor
    """
    # Flatten tensors for dot product
    low_flat = low.flatten()
    high_flat = high.flatten()

    # Normalize vectors
    low_norm = low_flat / torch.norm(low_flat)
    high_norm = high_flat / torch.norm(high_flat)

    # Compute angle between vectors
    dot = torch.clamp(torch.dot(low_norm, high_norm), -1.0, 1.0)
    omega = torch.acos(dot)

    # Handle near-parallel vectors (fall back to linear interpolation)
    if torch.abs(omega) < 1e-10:
        return low * (1.0 - val) + high * val

    # SLERP formula
    so = torch.sin(omega)
    result = (torch.sin((1.0 - val) * omega) / so) * low_flat + \
             (torch.sin(val * omega) / so) * high_flat

    return result.view(low.shape)

def lerp(val, low, high):
    """Simple linear interpolation (fallback)."""
    return low * (1.0 - val) + high * val

# =============================================================================
# Model Loading
# =============================================================================

def create_model():
    """Create the U-Net model architecture."""
    model = Unet(
        dim=BASE_CHANNELS,
        dim_mults=CHANNEL_MULTS,
        flash_attn=False,
        channels=3
    )
    return model

def load_model_from_checkpoint(checkpoint_path, device='cpu'):
    """
    Load the diffusion model from a training checkpoint.

    Uses EMA (Exponential Moving Average) weights for best quality,
    as these produce smoother and more stable outputs.

    Parameters:
        checkpoint_path: Path to model-X.pt checkpoint
        device: Device to load model on

    Returns:
        diffusion: GaussianDiffusion object with loaded weights
    """
    print(f"Loading checkpoint: {checkpoint_path}")

    # Create model architecture
    model = create_model()

    # Create diffusion process
    diffusion = GaussianDiffusion(
        model,
        image_size=IMAGE_SIZE,
        timesteps=TIMESTEPS,
        sampling_timesteps=SAMPLING_STEPS,
        objective='pred_noise'
    )

    # Load checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
    print(f"Checkpoint step: {checkpoint.get('step', 'unknown')}")

    # Extract EMA weights (these produce better quality than raw model weights)
    ema_state = checkpoint['ema']

    # Filter and rename EMA model keys
    # The EMA state has keys like "ema_model.betas", "ema_model.model.conv1.weight", etc.
    # We need to strip the "ema_model." prefix
    diffusion_state = {}
    for key, value in ema_state.items():
        if key.startswith('ema_model.'):
            new_key = key.replace('ema_model.', '')
            diffusion_state[new_key] = value

    # Load the EMA weights into the diffusion model
    diffusion.load_state_dict(diffusion_state)
    print("Loaded EMA weights successfully!")

    diffusion.to(device)
    diffusion.eval()

    return diffusion

# =============================================================================
# Frame Generation
# =============================================================================

@torch.no_grad()
def generate_from_noise(diffusion, noise, device):
    """
    Generate an image from a specific noise tensor using the reverse diffusion process.

    Parameters:
        diffusion: GaussianDiffusion model
        noise: Starting noise tensor [1, 3, H, W]
        device: Computation device

    Returns:
        image: Generated image as numpy array [H, W, 3] in range [0, 255]
    """
    noise = noise.to(device)

    # Get the model's sampling method with our specific noise
    # The library's ddim_sample uses shape to generate noise internally,
    # so we need to use p_sample_loop or implement custom sampling

    # Use the model's internal sampling with starting noise
    batch_size = noise.shape[0]
    shape = noise.shape

    # Get sampling parameters from diffusion model
    timesteps = diffusion.sampling_timesteps

    # Create time sequence for DDIM sampling
    times = torch.linspace(-1, diffusion.num_timesteps - 1, steps=timesteps + 1)
    times = list(reversed(times.int().tolist()))
    time_pairs = list(zip(times[:-1], times[1:]))

    img = noise.clone()

    for time, time_next in time_pairs:
        time_cond = torch.full((batch_size,), time, device=device, dtype=torch.long)

        # Predict noise
        pred_noise = diffusion.model(img, time_cond)

        # Get alpha values
        alpha = diffusion.alphas_cumprod[time]
        alpha_next = diffusion.alphas_cumprod[time_next] if time_next >= 0 else torch.tensor(1.0)

        # DDIM update step
        sigma = 0.0  # Deterministic sampling (no added noise)

        # Predict x0
        x0_pred = (img - torch.sqrt(1 - alpha) * pred_noise) / torch.sqrt(alpha)
        x0_pred = torch.clamp(x0_pred, -1, 1)

        # Calculate direction pointing to xt
        dir_xt = torch.sqrt(1 - alpha_next - sigma**2) * pred_noise

        # Update image
        if time_next < 0:
            img = x0_pred
        else:
            img = torch.sqrt(alpha_next) * x0_pred + dir_xt

    # Convert to numpy image
    img = img.cpu()
    img = (img + 1) / 2  # [-1, 1] -> [0, 1]
    img = img.clamp(0, 1)
    img = (img[0].permute(1, 2, 0).numpy() * 255).astype(np.uint8)

    return img

def generate_keyframe_noises(num_keyframes, shape, seed=None):
    """
    Generate random noise tensors for keyframes.

    Parameters:
        num_keyframes: Number of keyframe noises to generate
        shape: Shape of each noise tensor [1, C, H, W]
        seed: Random seed for reproducibility

    Returns:
        List of noise tensors
    """
    if seed is not None:
        torch.manual_seed(seed)

    noises = [torch.randn(shape) for _ in range(num_keyframes)]
    return noises

def interpolate_noises(noise1, noise2, num_steps):
    """
    Generate interpolated noise tensors between two keyframes using SLERP.

    Parameters:
        noise1: Starting noise
        noise2: Ending noise
        num_steps: Number of interpolation steps (excluding endpoints)

    Returns:
        List of interpolated noise tensors
    """
    interpolated = []
    for i in range(num_steps):
        t = i / num_steps  # Goes from 0 to just before 1
        interp_noise = slerp(t, noise1, noise2)
        interpolated.append(interp_noise)
    return interpolated

# =============================================================================
# GIF Creation
# =============================================================================

def upscale_image(img, target_size):
    """
    Upscale image using high-quality bicubic interpolation.

    Parameters:
        img: Image as numpy array [H, W, 3]
        target_size: Target dimension (square)

    Returns:
        Upscaled image as numpy array
    """
    pil_img = Image.fromarray(img)
    pil_img = pil_img.resize((target_size, target_size), Image.BICUBIC)
    return np.array(pil_img)

def create_gif(frames, output_path, fps):
    """
    Create a smooth, optimized GIF from frames.

    Parameters:
        frames: List of numpy arrays [H, W, 3]
        output_path: Output file path
        fps: Frames per second
    """
    print(f"\nCreating GIF with {len(frames)} frames at {fps} FPS...")

    # Save GIF using PIL for better optimization control
    pil_frames = [Image.fromarray(f) for f in frames]
    duration_ms = int(1000 / fps)

    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=True
    )

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Saved to: {output_path}")
    print(f"File size: {file_size:.2f} MB")
    print(f"Duration: {len(frames) / fps:.1f} seconds")

    # Try gifsicle for additional compression (if installed)
    import subprocess
    try:
        subprocess.run(
            ['gifsicle', '-O3', '--lossy=80', '--colors', '256',
             output_path, '-o', output_path],
            check=True, capture_output=True
        )
        optimized_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Optimized with gifsicle: {optimized_size:.2f} MB")
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass  # gifsicle not installed, PIL optimization is sufficient

# =============================================================================
# Main Generation
# =============================================================================

def generate_morph_animation():
    """Main function to generate the morphing animation."""
    print("=" * 60)
    print("DDPM Fabric Pattern Morphing Animation Generator")
    print("=" * 60)

    # Check for GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")

    if device == 'cpu':
        print("Warning: Generation on CPU will be slow (~30-60 minutes)")
        print("Consider using a GPU for faster generation (~10-15 minutes)")

    # Find best available checkpoint
    checkpoint_path = find_latest_checkpoint()
    if not os.path.exists(checkpoint_path):
        print(f"\nError: No checkpoint found at '{checkpoint_path}'")
        print("Please ensure training has completed (exercise3_train.py)")
        return

    # Load model
    diffusion = load_model_from_checkpoint(checkpoint_path, device)

    # Calculate frame counts
    total_frames = DURATION_SECONDS * FPS
    frames_per_transition = total_frames // NUM_KEYFRAMES
    actual_total_frames = frames_per_transition * NUM_KEYFRAMES

    print(f"\nAnimation parameters:")
    print(f"  - Duration: {DURATION_SECONDS} seconds")
    print(f"  - FPS: {FPS}")
    print(f"  - Keyframes: {NUM_KEYFRAMES}")
    print(f"  - Frames per transition: {frames_per_transition}")
    print(f"  - Total frames: {actual_total_frames}")
    print(f"  - Output size: {OUTPUT_SIZE}x{OUTPUT_SIZE}")
    print(f"  - DDIM sampling steps: {SAMPLING_STEPS}")

    # Generate keyframe noises
    print(f"\nGenerating {NUM_KEYFRAMES} keyframe noise vectors (seed={RANDOM_SEED})...")
    noise_shape = (1, 3, IMAGE_SIZE, IMAGE_SIZE)
    keyframe_noises = generate_keyframe_noises(NUM_KEYFRAMES, noise_shape, seed=RANDOM_SEED)

    # Generate all interpolated noises
    print("Creating interpolated noise sequence for seamless loop...")
    all_noises = []

    for i in range(NUM_KEYFRAMES):
        # Get current and next keyframe (wrap around for seamless loop)
        current_noise = keyframe_noises[i]
        next_noise = keyframe_noises[(i + 1) % NUM_KEYFRAMES]

        # Interpolate between them
        interpolated = interpolate_noises(current_noise, next_noise, frames_per_transition)
        all_noises.extend(interpolated)

    print(f"Total noise vectors: {len(all_noises)}")

    # Generate frames
    print(f"\nGenerating {len(all_noises)} frames...")
    frames = []

    for i, noise in enumerate(tqdm(all_noises, desc="Generating frames")):
        # Generate image from noise
        img = generate_from_noise(diffusion, noise, device)

        # Upscale to output size
        if OUTPUT_SIZE != IMAGE_SIZE:
            img = upscale_image(img, OUTPUT_SIZE)

        frames.append(img)

        # Clear GPU cache periodically
        if device == 'cuda' and i % 50 == 0:
            torch.cuda.empty_cache()

    # Create GIF
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    create_gif(frames, OUTPUT_PATH, FPS)

    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_PATH}")
    print("\nThe animation shows smooth morphing between fabric patterns,")
    print("demonstrating the DDPM model's learned representation space.")

# =============================================================================
# Entry Point
# =============================================================================

if __name__ == '__main__':
    generate_morph_animation()
