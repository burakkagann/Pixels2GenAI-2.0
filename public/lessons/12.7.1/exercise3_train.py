import os
import sys
import argparse
import time
from pathlib import Path

# Add current directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

# Import our Flow Matching model
try:
    from flow_model import SimpleFlowUNet, count_parameters
except ImportError:
    print("Error: flow_model.py not found in the same directory.")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

# Dataset configuration
DATASET_PATH = SCRIPT_DIR.parent.parent.parent / 'Module_12_generative_ai_models' / \
               '12.1_generative_adversarial_networks' / '12.1.2_dcgan_art' / \
               'african_fabric_dataset'

# Alternative: Direct path if the relative path doesn't work
# DATASET_PATH = Path(r"content/Module_12_generative_ai_models/12.1_generative_adversarial_networks/12.1.2_dcgan_art/african_fabric_dataset")

# Model configuration
IMAGE_SIZE = 64
BASE_CHANNELS = 64

# Training configuration
BATCH_SIZE = 32
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 0.01
NUM_STEPS = 100000         # Total training steps
LOG_EVERY = 100            # Log loss every N steps
SAMPLE_EVERY = 1000        # Generate samples every N steps
SAVE_EVERY = 5000          # Save checkpoint every N steps

# Output directories
MODELS_DIR = SCRIPT_DIR / 'models'
RESULTS_DIR = SCRIPT_DIR / 'training_results'

# =============================================================================
# Dataset
# =============================================================================

class AfricanFabricDataset(Dataset):
    """
    Dataset of African fabric patterns.

    Loads images from the DCGAN module's preprocessed dataset,
    enabling direct comparison between different generative approaches.
    """

    def __init__(self, data_dir, image_size=64):
        self.data_dir = Path(data_dir)
        self.image_size = image_size

        # Find all images
        self.image_paths = sorted(list(self.data_dir.glob('*.jpg')) +
                                  list(self.data_dir.glob('*.png')))

        if len(self.image_paths) == 0:
            raise ValueError(f"No images found in {data_dir}")

        print(f"Found {len(self.image_paths)} images")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        img_path = self.image_paths[idx]
        img = Image.open(img_path).convert('RGB')

        # Resize if needed
        if img.size != (self.image_size, self.image_size):
            img = img.resize((self.image_size, self.image_size), Image.LANCZOS)

        # Convert to tensor and normalize to [-1, 1]
        img = np.array(img).astype(np.float32) / 255.0
        img = (img - 0.5) / 0.5  # [0, 1] -> [-1, 1]
        img = torch.tensor(img).permute(2, 0, 1)  # [H, W, C] -> [C, H, W]

        return img

def create_dataloader(data_dir, batch_size=32, num_workers=2):
    """Create dataloader for training."""
    dataset = AfricanFabricDataset(data_dir, IMAGE_SIZE)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    return dataloader

# =============================================================================
# Flow Matching Training
# =============================================================================

def flow_matching_loss(model, x_1, device='cpu'):
    """
    Compute the Conditional Flow Matching loss.

    This is the core of Flow Matching training:
    1. Sample noise x_0 from N(0, I)
    2. Sample time t uniformly from [0, 1]
    3. Compute interpolation x_t = (1-t)*x_0 + t*x_1
    4. Target velocity is v_target = x_1 - x_0
    5. Predict velocity v_pred = model(x_t, t)
    6. Loss = MSE(v_pred, v_target)

    Parameters:
        model: Velocity prediction network
        x_1: Batch of data samples [B, C, H, W]
        device: Computation device

    Returns:
        loss: MSE loss between predicted and target velocity
    """
    batch_size = x_1.shape[0]

    # Step 1: Sample noise
    x_0 = torch.randn_like(x_1)

    # Step 2: Sample time uniformly from [0, 1]
    t = torch.rand(batch_size, device=device)

    # Step 3: Compute interpolation (straight path from x_0 to x_1)
    # Reshape t for broadcasting: [B] -> [B, 1, 1, 1]
    t_reshaped = t.view(-1, 1, 1, 1)
    x_t = (1 - t_reshaped) * x_0 + t_reshaped * x_1

    # Step 4: Target velocity (direction from noise to data)
    v_target = x_1 - x_0

    # Step 5: Predict velocity
    v_pred = model(x_t, t)

    # Step 6: MSE loss
    loss = F.mse_loss(v_pred, v_target)

    return loss

@torch.no_grad()
def sample_flow(model, num_samples, num_steps=50, device='cpu'):
    """
    Generate samples by integrating the learned velocity field.

    Parameters:
        model: Trained velocity network
        num_samples: Number of images to generate
        num_steps: ODE integration steps
        device: Computation device

    Returns:
        Generated images [N, C, H, W] in [-1, 1]
    """
    model.eval()

    # Start from noise
    x = torch.randn(num_samples, 3, IMAGE_SIZE, IMAGE_SIZE, device=device)

    # Euler integration
    dt = 1.0 / num_steps

    for i in range(num_steps):
        t = i / num_steps
        t_batch = torch.full((num_samples,), t, device=device)
        v = model(x, t_batch)
        x = x + dt * v

    x = x.clamp(-1, 1)
    return x

def create_sample_grid(samples, grid_size=4):
    """Create a grid of samples for visualization."""
    samples = (samples + 1) / 2  # [-1, 1] -> [0, 1]
    samples = samples.clamp(0, 1)
    samples = samples.cpu().numpy()

    n, c, h, w = samples.shape
    grid = np.zeros((c, h * grid_size, w * grid_size))

    for i in range(min(n, grid_size * grid_size)):
        row = i // grid_size
        col = i % grid_size
        grid[:, row*h:(row+1)*h, col*w:(col+1)*w] = samples[i]

    return grid.transpose(1, 2, 0)

# =============================================================================
# Training Loop
# =============================================================================

def train(args):
    """Main training function."""
    print("=" * 60)
    print("Flow Matching Training")
    print("=" * 60)

    # Setup device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    if device == 'cpu':
        print("\nWarning: Training on CPU will be very slow!")
        print("Consider using a GPU for faster training.")

    # Create output directories
    MODELS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    # Load dataset
    print(f"\nLoading dataset from: {DATASET_PATH}")
    try:
        dataloader = create_dataloader(DATASET_PATH, BATCH_SIZE, num_workers=0)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("\nPlease ensure the African fabric dataset exists at:")
        print(f"  {DATASET_PATH}")
        print("\nThis dataset should be available from Module 12.1.2 (DCGAN Art)")
        return

    # Save dataset preview
    print("Saving dataset preview...")
    data_iter = iter(dataloader)
    sample_batch = next(data_iter)
    grid = create_sample_grid(sample_batch[:9], grid_size=3)
    plt.figure(figsize=(6, 6))
    plt.imshow(grid)
    plt.axis('off')
    plt.title('Training Data Sample')
    plt.savefig(SCRIPT_DIR / 'training_samples_grid.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved training_samples_grid.png")

    # Create model
    model = SimpleFlowUNet(in_channels=3, base_channels=BASE_CHANNELS)
    model.to(device)
    print(f"\nModel parameters: {count_parameters(model):,}")

    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    # Training loop
    print(f"\nStarting training for {NUM_STEPS} steps...")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")

    losses = []
    step = 0
    start_time = time.time()

    # Load checkpoint if resuming
    checkpoint_path = MODELS_DIR / 'flow_matching_fabrics_latest.pt'
    if checkpoint_path.exists() and not args.fresh:
        print(f"\nResuming from checkpoint: {checkpoint_path}")
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        step = checkpoint['step']
        losses = checkpoint.get('losses', [])
        print(f"Resumed from step {step}")

    model.train()

    # Create infinite dataloader iterator
    def infinite_dataloader():
        while True:
            for batch in dataloader:
                yield batch

    data_iter = infinite_dataloader()

    try:
        pbar = tqdm(range(step, NUM_STEPS), initial=step, total=NUM_STEPS)

        for step in pbar:
            # Get batch
            x_1 = next(data_iter).to(device)

            # Compute loss
            loss = flow_matching_loss(model, x_1, device)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Logging
            losses.append(loss.item())

            if step % LOG_EVERY == 0:
                avg_loss = np.mean(losses[-100:]) if len(losses) >= 100 else np.mean(losses)
                pbar.set_postfix({'loss': f'{avg_loss:.4f}'})

            # Generate samples
            if step > 0 and step % SAMPLE_EVERY == 0:
                model.eval()
                samples = sample_flow(model, 16, num_steps=50, device=device)
                grid = create_sample_grid(samples)

                plt.figure(figsize=(8, 8))
                plt.imshow(grid)
                plt.axis('off')
                plt.title(f'Step {step}')
                plt.savefig(RESULTS_DIR / f'sample-{step // 1000}.png',
                            dpi=100, bbox_inches='tight')
                plt.close()

                model.train()

            # Save checkpoint
            if step > 0 and step % SAVE_EVERY == 0:
                checkpoint = {
                    'step': step,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'losses': losses
                }
                torch.save(checkpoint, checkpoint_path)
                print(f"\nSaved checkpoint at step {step}")

    except KeyboardInterrupt:
        print("\nTraining interrupted by user")

    # Save final model
    print("\nSaving final model...")
    final_path = MODELS_DIR / 'flow_matching_fabrics.pt'
    torch.save({
        'step': step,
        'model_state_dict': model.state_dict(),
        'losses': losses
    }, final_path)
    print(f"Saved model to {final_path}")

    # Save loss curve
    plt.figure(figsize=(10, 4))
    plt.plot(losses)
    plt.xlabel('Step')
    plt.ylabel('Loss')
    plt.title('Flow Matching Training Loss')
    plt.savefig(RESULTS_DIR / 'loss_curve.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved loss_curve.png")

    # Print summary
    elapsed = time.time() - start_time
    print(f"\nTraining complete!")
    print(f"Total steps: {step}")
    print(f"Total time: {elapsed / 3600:.2f} hours")
    print(f"Final loss: {np.mean(losses[-100:]):.4f}")

# =============================================================================
# Generate Samples from Checkpoints
# =============================================================================

def generate_samples(args):
    """Generate samples from saved checkpoints."""
    print("=" * 60)
    print("Generating Samples from Checkpoints")
    print("=" * 60)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Find checkpoints
    model_path = MODELS_DIR / 'flow_matching_fabrics.pt'

    if not model_path.exists():
        print(f"Error: Model not found at {model_path}")
        print("Please run training first with: python exercise3_train.py --train")
        return

    # Load model
    model = SimpleFlowUNet(in_channels=3, base_channels=BASE_CHANNELS)
    checkpoint = torch.load(model_path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()

    print(f"Loaded model from step {checkpoint.get('step', 'unknown')}")

    # Generate samples
    print("\nGenerating 16 samples...")
    samples = sample_flow(model, 16, num_steps=50, device=device)
    grid = create_sample_grid(samples)

    plt.figure(figsize=(10, 10))
    plt.imshow(grid)
    plt.axis('off')
    plt.title('Flow Matching Generated Samples')
    plt.savefig(SCRIPT_DIR / 'exercise3_final_samples.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("Saved exercise3_final_samples.png")

# =============================================================================
# Dataset Verification
# =============================================================================

def verify_dataset(args):
    """Verify the dataset exists and is accessible."""
    print("=" * 60)
    print("Dataset Verification")
    print("=" * 60)

    print(f"\nLooking for dataset at:")
    print(f"  {DATASET_PATH}")

    if not DATASET_PATH.exists():
        print(f"\nError: Dataset directory not found!")
        print("\nThe African fabric dataset should be located at:")
        print(f"  {DATASET_PATH}")
        print("\nThis dataset is created in Module 12.1.2 (DCGAN Art).")
        print("Please complete that module first, or copy the dataset here.")
        return False

    # Count images
    images = list(DATASET_PATH.glob('*.jpg')) + list(DATASET_PATH.glob('*.png'))

    if len(images) == 0:
        print("\nError: No images found in dataset directory!")
        return False

    print(f"\nFound {len(images)} images")

    # Check image format
    sample_img = Image.open(images[0])
    print(f"Sample image size: {sample_img.size}")
    print(f"Sample image mode: {sample_img.mode}")

    print("\nDataset verification successful!")
    print("You can proceed with training: python exercise3_train.py --train")

    return True

# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Flow Matching Training')

    parser.add_argument('--verify', action='store_true',
                        help='Verify dataset exists')
    parser.add_argument('--train', action='store_true',
                        help='Start or resume training')
    parser.add_argument('--samples', action='store_true',
                        help='Generate samples from trained model')
    parser.add_argument('--fresh', action='store_true',
                        help='Start fresh training (ignore checkpoints)')
    parser.add_argument('--steps', type=int, default=None,
                        help='Override number of training steps')

    args = parser.parse_args()

    # Override num steps if specified
    global NUM_STEPS
    if args.steps is not None:
        NUM_STEPS = args.steps

    if args.verify:
        verify_dataset(args)
    elif args.train:
        if not verify_dataset(args):
            return
        train(args)
    elif args.samples:
        generate_samples(args)
    else:
        print("Flow Matching Training Script")
        print("=" * 40)
        print("\nUsage:")
        print("  python exercise3_train.py --verify   # Check dataset")
        print("  python exercise3_train.py --train    # Start training")
        print("  python exercise3_train.py --samples  # Generate from model")
        print("\nOptional flags:")
        print("  --fresh                # Start fresh (ignore checkpoints)")
        print("  --steps N              # Set number of training steps")
        print("\nExample:")
        print("  python exercise3_train.py --train --steps 10000")

if __name__ == '__main__':
    main()
