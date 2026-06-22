import os
import sys
from pathlib import Path

# Add current directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Import our Flow Matching model
try:
    from flow_model import SimpleFlowUNet, count_parameters
except ImportError:
    print("Error: flow_model.py not found in the same directory.")
    print("Please ensure flow_model.py exists alongside this script.")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

# Model parameters (must match training configuration)
IMAGE_SIZE = 64
BASE_CHANNELS = 64

# Model checkpoint path
MODEL_PATH = SCRIPT_DIR / 'models' / 'flow_matching_fabrics.pt'

# Generation settings
NUM_SAMPLES = 16         # Number of images to generate
SAMPLING_STEPS = 50      # ODE integration steps (10-50 typical for FM)
RANDOM_SEED = 42         # For reproducible results

# =============================================================================
# Flow Matching Sampling (ODE Integration)
# =============================================================================

@torch.no_grad()
def sample_flow(model, num_samples, num_steps=50, device='cpu'):
    """
    Generate samples by integrating the learned velocity field.

    This is the core of Flow Matching: we start from pure noise (t=0)
    and follow the velocity field to reach the data distribution (t=1).

    The integration uses the Euler method:
        x_{t+dt} = x_t + dt * v(x_t, t)

    Parameters:
        model: Trained velocity network v(x, t)
        num_samples: Number of images to generate
        num_steps: ODE integration steps (fewer = faster, more = better)
        device: Device to run on

    Returns:
        Generated images as numpy array [N, C, H, W]
    """
    model.eval()

    # Start from pure Gaussian noise (t=0)
    x = torch.randn(num_samples, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)

    # Time step size
    dt = 1.0 / num_steps

    print(f"Integrating flow from t=0 (noise) to t=1 (data)...")
    print(f"Using {num_steps} Euler steps")

    # Euler integration from t=0 to t=1
    for i in range(num_steps):
        # Current time
        t = i / num_steps
        t_batch = torch.full((num_samples,), t, device=device)

        # Get velocity at current position and time
        v = model(x, t_batch)

        # Euler step: move in direction of velocity
        x = x + dt * v

        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"  Step {i + 1}/{num_steps}")

    # Clamp to valid range
    x = x.clamp(-1, 1)

    # Convert to numpy
    x = x.cpu().numpy()

    return x

# =============================================================================
# Model Loading
# =============================================================================

def load_model(model_path, device='cpu'):
    """
    Load the trained Flow Matching model.

    Parameters:
        model_path: Path to saved model weights
        device: Device to load model on

    Returns:
        model: Loaded SimpleFlowUNet model
    """
    # Create model architecture
    model = SimpleFlowUNet(
        in_channels=3,
        base_channels=BASE_CHANNELS
    )

    print(f"Model parameters: {count_parameters(model):,}")

    # Load weights
    if os.path.exists(model_path):
        print(f"Loading model from: {model_path}")
        checkpoint = torch.load(model_path, map_location=device, weights_only=True)

        # Handle different checkpoint formats
        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)

        print("Model loaded successfully!")
    else:
        print(f"Warning: Model file not found at '{model_path}'")
        print("\nTo use this script, you need to either:")
        print("1. Complete Exercise 3 to train your own model")
        print("2. Download pre-trained weights (when available)")
        print("\n[PLACEHOLDER: Pre-trained weights will be available after training]")
        print("\nUsing randomly initialized weights (output will be noise)")

    model.to(device)
    model.eval()

    return model

# =============================================================================
# Visualization
# =============================================================================

def create_grid(samples, grid_size=4):
    """
    Arrange samples into a grid image.

    Parameters:
        samples: Array of images [N, C, H, W] in range [-1, 1]
        grid_size: Grid dimensions (grid_size x grid_size)

    Returns:
        grid: Single image containing all samples [H, W, C] in [0, 1]
    """
    # Denormalize from [-1, 1] to [0, 1]
    samples = (samples + 1) / 2
    samples = np.clip(samples, 0, 1)

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
        samples: Array of images [N, C, H, W] in range [-1, 1]
        output_dir: Directory to save images
    """
    output_path = SCRIPT_DIR / output_dir
    output_path.mkdir(exist_ok=True)

    # Denormalize
    samples = (samples + 1) / 2
    samples = np.clip(samples, 0, 1)

    for i, sample in enumerate(samples):
        img = (sample.transpose(1, 2, 0) * 255).astype(np.uint8)
        img = Image.fromarray(img)
        img.save(output_path / f'fabric_{i:04d}.png')

    print(f"Saved {len(samples)} images to '{output_path}/'")

# =============================================================================
# Main
# =============================================================================

def main():
    """Main generation function."""
    print("=" * 60)
    print("Flow Matching African Fabric Pattern Generator")
    print("=" * 60)

    # Check for GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nDevice: {device}")

    # Set random seed for reproducibility
    torch.manual_seed(RANDOM_SEED)
    if device == 'cuda':
        torch.cuda.manual_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # Load model
    model = load_model(MODEL_PATH, device)

    # Generate samples
    print(f"\nGenerating {NUM_SAMPLES} samples with {SAMPLING_STEPS} steps...")
    samples = sample_flow(model, NUM_SAMPLES, SAMPLING_STEPS, device)

    print(f"\nGenerated {len(samples)} fabric patterns")

    # Create and save grid
    grid_size = int(np.ceil(np.sqrt(NUM_SAMPLES)))
    grid = create_grid(samples, grid_size)

    plt.figure(figsize=(10, 10))
    plt.imshow(grid)
    plt.axis('off')
    plt.title('Flow Matching Generated African Fabric Patterns\n'
              f'({SAMPLING_STEPS} integration steps)', fontsize=14)
    plt.tight_layout()

    output_file = SCRIPT_DIR / 'exercise1_output.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved grid to '{output_file}'")

    # Also save individual samples
    save_individual_samples(samples)

    # Print comparison with DDPM
    print("\n" + "=" * 60)
    print("Comparison with DDPM (Module 12.3.1)")
    print("=" * 60)
    print(f"""
Flow Matching:  {SAMPLING_STEPS} steps to generate images
DDPM:          250 steps (with DDIM acceleration)
               1000 steps (full diffusion)

Key Insight: Flow Matching follows STRAIGHT paths from noise to data,
while diffusion follows CURVED, noisy trajectories.

Straight paths are easier to integrate with fewer steps!
    """)

    # Print reflection questions
    print("=" * 60)
    print("Reflection Questions")
    print("=" * 60)
    print("""
1. How do these Flow Matching patterns compare to DDPM output
   from Module 12.3.1? Consider:
   - Generation speed (50 steps vs 250 steps)
   - Visual quality and coherence
   - Pattern diversity

2. Flow Matching uses ODE integration (deterministic) while DDPM
   uses SDE (stochastic). What might be the implications of this?

3. Try changing SAMPLING_STEPS to 10, 20, or 100. How does quality
   change? At what point do you see diminishing returns?

4. The same U-Net architecture works for both DDPM and Flow Matching.
   Why might this be? What's the key difference in what it learns?
    """)

if __name__ == '__main__':
    main()
