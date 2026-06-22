import os
import sys
from pathlib import Path

# Add current directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from PIL import Image

try:
    import imageio.v2 as imageio
    HAS_IMAGEIO = True
except ImportError:
    HAS_IMAGEIO = False
    print("Note: imageio not found. GIF creation will be skipped.")
    print("Install with: pip install imageio")

# Import our Flow Matching model
try:
    from flow_model import SimpleFlowUNet, count_parameters
except ImportError:
    print("Error: flow_model.py not found in the same directory.")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

IMAGE_SIZE = 64
BASE_CHANNELS = 64
MODEL_PATH = SCRIPT_DIR / 'models' / 'flow_matching_fabrics.pt'
RANDOM_SEED = 42

# =============================================================================
# Core Flow Matching Functions
# =============================================================================

@torch.no_grad()
def sample_flow_with_trajectory(model, num_samples, num_steps, device='cpu',
                                capture_times=None):
    """
    Generate samples while capturing intermediate states.

    This version records the trajectory from noise to image,
    allowing us to visualize the flow.

    Parameters:
        model: Trained velocity network
        num_samples: Number of images to generate
        num_steps: Integration steps
        device: Computation device
        capture_times: List of times (0-1) to capture (None = all steps)

    Returns:
        final_samples: Generated images [N, C, H, W]
        trajectory: Dict mapping time -> images at that time
    """
    model.eval()

    # Default: capture every 10% of progress
    if capture_times is None:
        capture_times = [i / 10 for i in range(11)]

    trajectory = {}

    # Start from noise
    x = torch.randn(num_samples, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
    trajectory[0.0] = x.detach().cpu().numpy().copy()

    dt = 1.0 / num_steps

    for i in range(num_steps):
        t = i / num_steps
        t_batch = torch.full((num_samples,), t, device=device)

        # Get velocity and step
        v = model(x, t_batch)
        x = x + dt * v

        # Capture at specified times
        for capture_t in capture_times:
            if abs((i + 1) / num_steps - capture_t) < dt / 2:
                trajectory[capture_t] = x.detach().cpu().numpy().copy()

    x = x.clamp(-1, 1)
    trajectory[1.0] = x.detach().cpu().numpy().copy()

    return x.detach().cpu().numpy(), trajectory

@torch.no_grad()
def compute_velocity_field(model, x, t, device='cpu'):
    """
    Compute velocity field at a given position and time.

    Parameters:
        model: Trained velocity network
        x: Input images [N, C, H, W]
        t: Time value (scalar)

    Returns:
        velocity: Velocity field [N, C, H, W]
    """
    model.eval()
    x = torch.tensor(x, dtype=torch.float32, device=device)
    t_batch = torch.full((x.shape[0],), t, device=device)
    v = model(x, t_batch)
    return v.detach().cpu().numpy()

# =============================================================================
# Part A: Sampling Steps Comparison
# =============================================================================

def visualize_steps_comparison(model, device='cpu'):
    """
    Compare generation quality at different step counts.

    This demonstrates the key advantage of Flow Matching:
    it produces good results with far fewer steps than diffusion.
    """
    print("\n" + "=" * 60)
    print("Part A: Sampling Steps Comparison")
    print("=" * 60)

    step_counts = [5, 10, 20, 50, 100]

    # Fix random seed for fair comparison
    torch.manual_seed(RANDOM_SEED)

    # Store results
    results = {}

    with torch.no_grad():
        for steps in step_counts:
            print(f"  Generating with {steps} steps...")

            # Reset seed for identical starting noise
            torch.manual_seed(RANDOM_SEED)

            # Generate one sample
            x = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)
            dt = 1.0 / steps

            for i in range(steps):
                t = i / steps
                t_batch = torch.full((1,), t, device=device)
                v = model(x, t_batch)
                x = x + dt * v

            x = x.clamp(-1, 1)
            results[steps] = x.detach().cpu().numpy()[0]

    # Create comparison figure
    fig, axes = plt.subplots(1, len(step_counts), figsize=(15, 3))

    for i, steps in enumerate(step_counts):
        img = (results[steps].transpose(1, 2, 0) + 1) / 2
        img = np.clip(img, 0, 1)
        axes[i].imshow(img)
        axes[i].set_title(f'{steps} steps', fontsize=12)
        axes[i].axis('off')

    plt.suptitle('Flow Matching: Quality vs Number of Integration Steps',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = SCRIPT_DIR / 'exercise2_steps_comparison.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\nSaved comparison to '{output_file}'")
    print("\nKey Insight: Flow Matching produces usable results with just 10-20 steps!")
    print("Compare this to DDPM which typically needs 250-1000 steps.")

# =============================================================================
# Part B: Flow Trajectory Visualization
# =============================================================================

def visualize_flow_trajectory(model, device='cpu'):
    """
    Visualize the path from noise to image.

    Shows how Flow Matching follows a (nearly) straight path
    from the noise distribution to the data distribution.
    """
    print("\n" + "=" * 60)
    print("Part B: Flow Trajectory Visualization")
    print("=" * 60)

    # Times to capture
    capture_times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    torch.manual_seed(RANDOM_SEED)

    # Generate with trajectory
    _, trajectory = sample_flow_with_trajectory(
        model, num_samples=1, num_steps=100,
        device=device, capture_times=capture_times
    )

    # Create figure
    fig, axes = plt.subplots(1, len(capture_times), figsize=(18, 2))

    for i, t in enumerate(capture_times):
        if t in trajectory:
            img = (trajectory[t][0].transpose(1, 2, 0) + 1) / 2
            img = np.clip(img, 0, 1)
            axes[i].imshow(img)
        axes[i].set_title(f't={t:.1f}', fontsize=10)
        axes[i].axis('off')

    plt.suptitle('Flow Trajectory: From Noise (t=0) to Image (t=1)',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = SCRIPT_DIR / 'exercise2_flow_trajectory.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved trajectory to '{output_file}'")

    # Create GIF if imageio is available
    if HAS_IMAGEIO:
        print("Creating animated GIF...")

        # Design: Fast transition (2 sec) + hold on final fabric (2 sec) = 4 sec total
        # 60 transition frames + 60 hold frames = 120 frames at 30 FPS = 4 seconds
        torch.manual_seed(RANDOM_SEED)
        _, full_trajectory = sample_flow_with_trajectory(
            model, num_samples=1, num_steps=60,
            device=device, capture_times=[i / 60 for i in range(61)]
        )

        frames = []

        # Add transition frames (noise → fabric)
        for t in sorted(full_trajectory.keys()):
            img = (full_trajectory[t][0].transpose(1, 2, 0) + 1) / 2
            img = np.clip(img, 0, 1)
            img = (img * 255).astype(np.uint8)
            frames.append(img)

        # Hold the final fabric pattern for 2 seconds (60 frames at 30 FPS)
        final_frame = frames[-1]
        for _ in range(60):
            frames.append(final_frame)

        gif_file = SCRIPT_DIR / 'exercise2_flow_trajectory.gif'
        imageio.mimsave(gif_file, frames, fps=30, loop=0)
        duration = len(frames) / 30
        print(f"Saved animation to '{gif_file}' ({len(frames)} frames at 30 FPS = {duration:.1f} sec)")
    else:
        print("Skipping GIF creation (imageio not installed)")

# =============================================================================
# Part C: Velocity Field Visualization
# =============================================================================

def visualize_velocity_field(model, device='cpu'):
    """
    Visualize the learned velocity field at different times.

    The velocity field shows which direction the flow is "pushing"
    samples at each point in the trajectory.
    """
    print("\n" + "=" * 60)
    print("Part C: Velocity Field Visualization")
    print("=" * 60)

    torch.manual_seed(RANDOM_SEED)

    # Generate a trajectory first
    _, trajectory = sample_flow_with_trajectory(
        model, num_samples=1, num_steps=50,
        device=device, capture_times=[0.0, 0.25, 0.5, 0.75, 1.0]
    )

    times_to_show = [0.0, 0.25, 0.5, 0.75]

    fig = plt.figure(figsize=(16, 8))
    gs = GridSpec(2, 4, figure=fig)

    for i, t in enumerate(times_to_show):
        if t not in trajectory:
            continue

        x = trajectory[t]

        # Compute velocity at this point
        v = compute_velocity_field(model, x, t, device)

        # Top row: current state
        ax1 = fig.add_subplot(gs[0, i])
        img = (x[0].transpose(1, 2, 0) + 1) / 2
        img = np.clip(img, 0, 1)
        ax1.imshow(img)
        ax1.set_title(f'State at t={t:.2f}', fontsize=11)
        ax1.axis('off')

        # Bottom row: velocity magnitude
        ax2 = fig.add_subplot(gs[1, i])

        # Compute velocity magnitude per pixel
        v_magnitude = np.sqrt(np.sum(v[0] ** 2, axis=0))

        im = ax2.imshow(v_magnitude, cmap='hot')
        ax2.set_title(f'Velocity magnitude', fontsize=11)
        ax2.axis('off')

    plt.suptitle('Flow Matching: State and Velocity Field at Different Times',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = SCRIPT_DIR / 'exercise2_velocity_field.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved velocity field visualization to '{output_file}'")
    print("\nKey Insight: Early in the flow (t near 0), velocities are large")
    print("as the flow pushes noise toward the data distribution.")
    print("Later (t near 1), velocities become smaller as we approach the target.")

# =============================================================================
# Model Loading
# =============================================================================

def load_model(model_path, device='cpu'):
    """Load the trained Flow Matching model."""
    model = SimpleFlowUNet(in_channels=3, base_channels=BASE_CHANNELS)

    if os.path.exists(model_path):
        print(f"Loading model from: {model_path}")
        checkpoint = torch.load(model_path, map_location=device, weights_only=True)

        if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)

        print("Model loaded successfully!")
    else:
        print(f"Warning: Model not found at '{model_path}'")
        print("[PLACEHOLDER: Train model using exercise3_train.py first]")
        print("Using random weights for demonstration...")

    model.to(device)
    model.eval()
    return model

# =============================================================================
# Main
# =============================================================================

def main():
    """Run all three explorations."""
    print("=" * 60)
    print("Flow Matching Parameter Exploration")
    print("=" * 60)

    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Load model
    model = load_model(MODEL_PATH, device)

    # Run explorations
    visualize_steps_comparison(model, device)
    visualize_flow_trajectory(model, device)
    visualize_velocity_field(model, device)

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("""
Three visualizations have been created:

1. exercise2_steps_comparison.png
   Shows how quality changes with different step counts (5, 10, 20, 50, 100).
   Key finding: Flow Matching works well with just 10-20 steps!

2. exercise2_flow_trajectory.png (and .gif if imageio installed)
   Shows the path from noise (t=0) to image (t=1).
   Key finding: The transformation is gradual and smooth.

3. exercise2_velocity_field.png
   Shows the learned velocity field at different times.
   Key finding: Velocity magnitude decreases as we approach t=1.
    """)

    print("\n" + "=" * 60)
    print("Suggested Modifications")
    print("=" * 60)
    print("""
Try these experiments to deepen your understanding:

1. Change RANDOM_SEED to see different patterns

2. In visualize_steps_comparison():
   - Try step_counts = [1, 2, 3, 5, 10] for very low steps
   - Compare with DDPM at the same step counts

3. In visualize_flow_trajectory():
   - Change num_steps to see coarser/finer trajectories
   - Try with multiple samples to see variance

4. In visualize_velocity_field():
   - Visualize velocity direction as arrows (quiver plot)
   - Compare velocity patterns across different generated images
    """)

if __name__ == '__main__':
    main()
