import torch
from stylegan2_pytorch import Trainer
import os
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# Dataset path (relative to this script's location)
DATA_PATH = str(SCRIPT_DIR / '..' / '12.1.2_dcgan_art' / 'african_fabric_processed')

# Output directories (in the same folder as this script)
RESULTS_DIR = str(SCRIPT_DIR / 'training_results')
CHECKPOINTS_DIR = str(SCRIPT_DIR / 'models')

# Training hyperparameters
IMAGE_SIZE = 64  # Match the dataset resolution
BATCH_SIZE = 16  # Adjust based on GPU memory
GRADIENT_ACCUMULATE_EVERY = 4  # Effective batch size = BATCH_SIZE * GRADIENT_ACCUMULATE_EVERY
LEARNING_RATE = 2e-4  # StyleGAN2 default
NUM_TRAIN_STEPS = 10000  # Adjust based on time constraints (2000-10000 recommended)

# Checkpoint settings
SAVE_EVERY = 100  # Save checkpoint every N steps
GENERATE_SAMPLES_EVERY = 100  # Generate sample images every N steps

# =============================================================================
# Verify Dataset
# =============================================================================

def verify_dataset():
    """Check if dataset exists and count images."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}\n"
            f"Please ensure the African fabric dataset from Module 12.1.2 is available."
        )

    # Count PNG files in dataset
    image_files = [f for f in os.listdir(DATA_PATH) if f.endswith(('.png', '.jpg', '.jpeg'))]
    num_images = len(image_files)

    if num_images == 0:
        raise ValueError(f"No images found in {DATA_PATH}")

    print(f"Dataset verified: {num_images} images found")
    return num_images

# =============================================================================
# Main Training
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("StyleGAN2 Training on African Fabric Patterns")
    print("=" * 60)

    # Verify dataset
    print("\nStep 1: Verifying dataset...")
    num_images = verify_dataset()

    # Check GPU availability
    print("\nStep 2: Checking GPU availability...")
    if torch.cuda.is_available():
        print(f"  GPU detected: {torch.cuda.get_device_name(0)}")
        print(f"  GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    else:
        print("  WARNING: No GPU detected. Training on CPU will be very slow.")
        print("  Consider using Google Colab or a cloud GPU if training takes too long.")

    # Initialize trainer
    print("\nStep 3: Initializing StyleGAN2 trainer...")
    trainer = Trainer(
        name='african_fabrics',
        results_dir=RESULTS_DIR,
        models_dir=CHECKPOINTS_DIR,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        gradient_accumulate_every=GRADIENT_ACCUMULATE_EVERY,
        lr=LEARNING_RATE,
        save_every=SAVE_EVERY
    )

    # Set the data source (required before training)
    trainer.set_data_src(DATA_PATH)

    print(f"  Model name: african_fabrics")
    print(f"  Image size: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print(f"  Batch size: {BATCH_SIZE}")
    print(f"  Effective batch size: {BATCH_SIZE * GRADIENT_ACCUMULATE_EVERY}")
    print(f"  Learning rate: {LEARNING_RATE}")

    # Training info
    print("\nStep 4: Starting training...")
    print(f"  Total training steps: {NUM_TRAIN_STEPS}")
    print(f"  Checkpoints will be saved every {SAVE_EVERY} steps")
    print(f"  Sample images will be generated every {GENERATE_SAMPLES_EVERY} steps")

    estimated_time_hours = (NUM_TRAIN_STEPS / 1000) * 0.5  # Rough estimate: 30 min per 1000 steps on GPU
    print(f"  Estimated time: ~{estimated_time_hours:.1f} hours on a modern GPU")
    print("\nPress Ctrl+C to stop training early and use the last checkpoint.")
    print("-" * 60)

    # Training loop - train() runs one step at a time
    try:
        from tqdm import tqdm
        for step in tqdm(range(NUM_TRAIN_STEPS), desc="Training"):
            trainer.train()
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print(f"Training interrupted by user at step {trainer.steps}")
        print("=" * 60)

    # Training complete
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nCheckpoints saved in: {CHECKPOINTS_DIR}")
    print(f"Sample images saved in: {RESULTS_DIR}")
