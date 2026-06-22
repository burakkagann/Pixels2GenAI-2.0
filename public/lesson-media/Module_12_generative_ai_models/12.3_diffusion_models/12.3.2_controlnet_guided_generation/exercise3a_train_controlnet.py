import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image
from pathlib import Path
import json
import argparse
from tqdm import tqdm

# Script configuration
SCRIPT_DIR = Path(__file__).parent
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Training hyperparameters (configured for extended training ~20-24 hours)
BATCH_SIZE = 4  # Batch size for training
LEARNING_RATE = 5e-6  # Lower LR for longer, more stable training
MAX_TRAIN_STEPS = 10000  # Extended training for better results
GRADIENT_ACCUMULATION_STEPS = 1  # Set to 1 for standard training
IMAGE_SIZE = 512
SAVE_STEPS = 500  # More frequent checkpoints to minimize loss on crash
SAMPLE_STEPS = 1000  # Generate samples every 1000 steps
LOG_STEPS = 50
MAX_SAMPLES = None  # Use full dataset (50,000 samples)
LR_WARMUP_STEPS = 500  # Warmup for stable training start
RESUME_CHECKPOINT = None  # Set to step number to resume (e.g., 2000)

# Paths
DATASET_DIR = SCRIPT_DIR / 'fill50k'
OUTPUT_DIR = SCRIPT_DIR / 'training_results' / 'fill50k'
MODEL_DIR = SCRIPT_DIR / 'models'

class Fill50KDataset(Dataset):
    """
    Fill50K Dataset for ControlNet training.

    Each sample consists of:
    - source: Circle outline image (conditioning)
    - target: Filled shape image (ground truth)
    - prompt: Text description

    Reference: https://github.com/lllyasviel/ControlNet
    """

    def __init__(self, data_dir, image_size=512, max_samples=None):
        self.data_dir = Path(data_dir)
        self.image_size = image_size

        # Load metadata
        prompt_file = self.data_dir / 'prompt.json'
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self.data_dir}\n"
                "Please run: python download_fill50k.py"
            )

        with open(prompt_file, 'r') as f:
            # Handle both JSON array and JSONL formats
            content = f.read().strip()
            if content.startswith('['):
                # Standard JSON array
                self.metadata = json.loads(content)
            else:
                # JSONL format (one JSON object per line)
                self.metadata = [json.loads(line) for line in content.split('\n') if line.strip()]

        # Limit samples for faster training (demonstration purposes)
        if max_samples and len(self.metadata) > max_samples:
            self.metadata = self.metadata[:max_samples]
            print(f"Using {max_samples} samples (subset) for demonstration")

        print(f"Loaded {len(self.metadata)} training samples from Fill50K")

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        item = self.metadata[idx]

        # Load source (conditioning) image
        # Handle both "0.png" and "source/0.png" path formats
        source_file = item['source']
        if source_file.startswith('source/'):
            source_path = self.data_dir / source_file
        else:
            source_path = self.data_dir / 'source' / source_file
        source = Image.open(source_path).convert('RGB')
        source = source.resize((self.image_size, self.image_size), Image.LANCZOS)

        # Load target (ground truth) image
        target_file = item['target']
        if target_file.startswith('target/'):
            target_path = self.data_dir / target_file
        else:
            target_path = self.data_dir / 'target' / target_file
        target = Image.open(target_path).convert('RGB')
        target = target.resize((self.image_size, self.image_size), Image.LANCZOS)

        # Convert to tensors (normalize to [-1, 1])
        source_tensor = torch.from_numpy(np.array(source)).float() / 127.5 - 1
        source_tensor = source_tensor.permute(2, 0, 1)  # HWC -> CHW

        target_tensor = torch.from_numpy(np.array(target)).float() / 127.5 - 1
        target_tensor = target_tensor.permute(2, 0, 1)

        return {
            'conditioning': source_tensor,
            'target': target_tensor,
            'prompt': item['prompt']
        }

def verify_dataset():
    """Verify the Fill50K dataset exists and is properly formatted."""
    print("Verifying Fill50K dataset...")

    if not DATASET_DIR.exists():
        print(f"Dataset directory not found: {DATASET_DIR}")
        print()
        print("Please download the Fill50K dataset:")
        print("  python download_fill50k.py")
        print()
        print("Or manually download from:")
        print("  https://huggingface.co/lllyasviel/ControlNet/tree/main/training")
        return False

    # Check required files
    required = ['prompt.json', 'source', 'target']
    for item in required:
        path = DATASET_DIR / item
        if not path.exists():
            print(f"Missing: {path}")
            return False

    # Load and verify metadata
    try:
        with open(DATASET_DIR / 'prompt.json', 'r') as f:
            content = f.read().strip()
            if content.startswith('['):
                metadata = json.loads(content)
            else:
                # JSONL format (one JSON object per line)
                metadata = [json.loads(line) for line in content.split('\n') if line.strip()]
        print(f"Found {len(metadata)} training samples")
    except Exception as e:
        print(f"Error reading metadata: {e}")
        return False

    # Check sample images
    source_dir = DATASET_DIR / 'source'
    target_dir = DATASET_DIR / 'target'

    source_count = len(list(source_dir.glob('*.png')))
    target_count = len(list(target_dir.glob('*.png')))

    print(f"Source images: {source_count}")
    print(f"Target images: {target_count}")

    if source_count == 0 or target_count == 0:
        print("No images found in source/target directories")
        return False

    print()
    print("Dataset verification: PASSED")
    return True

def train_controlnet():
    """
    Train ControlNet from scratch on Fill50K.

    This implements the core ControlNet training loop:
    1. Load pretrained Stable Diffusion as base
    2. Create ControlNet adapter with zero convolutions
    3. Freeze SD weights, train only ControlNet
    4. Use same noise prediction loss as DDPM
    """
    print("=" * 60)
    print("ControlNet Training on Fill50K")
    print("=" * 60)
    print()

    # Check CUDA availability
    if DEVICE != 'cuda':
        print("WARNING: Training on CPU will be very slow.")
        print("GPU is highly recommended for ControlNet training.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    print(f"Device: {DEVICE}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Max training steps: {MAX_TRAIN_STEPS}")
    if MAX_SAMPLES:
        print(f"Dataset samples: {MAX_SAMPLES} (subset)")
    else:
        print(f"Dataset samples: all (full 50K)")
    if RESUME_CHECKPOINT:
        print(f"Resume from: step {RESUME_CHECKPOINT}")
    print()

    # Verify dataset
    if not verify_dataset():
        return

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Import training libraries
    try:
        from diffusers import (
            ControlNetModel,
            StableDiffusionControlNetPipeline,
            DDPMScheduler,
            AutoencoderKL,
            UNet2DConditionModel
        )
        from transformers import CLIPTextModel, CLIPTokenizer, get_cosine_schedule_with_warmup
        from accelerate import Accelerator
    except ImportError:
        print("Required libraries not found.")
        print("Please install:")
        print("  pip install diffusers transformers accelerate")
        return

    print("Loading pretrained models...")

    # Initialize accelerator for distributed training support
    accelerator = Accelerator(
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        mixed_precision='fp16' if DEVICE == 'cuda' else 'no'
    )

    # Load tokenizer and text encoder
    tokenizer = CLIPTokenizer.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="tokenizer"
    )
    text_encoder = CLIPTextModel.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="text_encoder"
    )

    # Load VAE
    vae = AutoencoderKL.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="vae"
    )

    # Load U-Net (frozen during training)
    unet = UNet2DConditionModel.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="unet"
    )

    # Create ControlNet (this is what we train)
    controlnet = ControlNetModel.from_unet(unet)

    # Freeze non-ControlNet weights
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)
    unet.requires_grad_(False)

    # Only ControlNet is trainable
    controlnet.train()

    # Count parameters
    trainable_params = sum(p.numel() for p in controlnet.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in controlnet.parameters())
    print(f"ControlNet parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")

    # Create dataset and dataloader (using subset for demonstration)
    dataset = Fill50KDataset(DATASET_DIR, image_size=IMAGE_SIZE, max_samples=MAX_SAMPLES)
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,  # Set to 0 for Windows compatibility
        pin_memory=True if DEVICE == 'cuda' else False
    )

    # Noise scheduler (same as DDPM)
    noise_scheduler = DDPMScheduler.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="scheduler"
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        controlnet.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.01
    )

    # Learning rate scheduler (cosine with warmup for stable long training)
    lr_scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=LR_WARMUP_STEPS,
        num_training_steps=MAX_TRAIN_STEPS
    )

    # Prepare for training
    controlnet, optimizer, dataloader, lr_scheduler = accelerator.prepare(
        controlnet, optimizer, dataloader, lr_scheduler
    )
    vae.to(accelerator.device)
    text_encoder.to(accelerator.device)
    unet.to(accelerator.device)

    # Resume from checkpoint if specified
    global_step = 0
    loss_history = []

    if RESUME_CHECKPOINT:
        checkpoint_path = OUTPUT_DIR / f'checkpoint-{RESUME_CHECKPOINT}'
        if checkpoint_path.exists():
            print(f"Resuming from checkpoint: {checkpoint_path}")
            accelerator.load_state(checkpoint_path)
            global_step = RESUME_CHECKPOINT
            print(f"Resumed at step {global_step}")
        else:
            print(f"WARNING: Checkpoint not found at {checkpoint_path}")
            print("Starting from scratch...")

    # Estimate training time
    steps_remaining = MAX_TRAIN_STEPS - global_step
    estimated_hours = (steps_remaining * 11.64) / 3600  # ~11.64s per step from previous run
    print()
    print("Starting training...")
    print(f"Training from step {global_step} to {MAX_TRAIN_STEPS} ({steps_remaining} steps)")
    print(f"Estimated time: {estimated_hours:.1f} hours")
    print(f"LR scheduler: cosine with {LR_WARMUP_STEPS} warmup steps")
    print("-" * 60)

    progress_bar = tqdm(total=MAX_TRAIN_STEPS, initial=global_step, desc="Training ControlNet")

    while global_step < MAX_TRAIN_STEPS:
        for batch in dataloader:
            if global_step >= MAX_TRAIN_STEPS:
                break

            # Get batch data
            conditioning = batch['conditioning'].to(accelerator.device)
            target = batch['target'].to(accelerator.device)
            prompts = batch['prompt']

            # Encode target images to latent space
            with torch.no_grad():
                latents = vae.encode(target).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

            # Sample noise
            noise = torch.randn_like(latents)

            # Sample timesteps
            batch_size = latents.shape[0]
            timesteps = torch.randint(
                0, noise_scheduler.config.num_train_timesteps,
                (batch_size,), device=accelerator.device
            ).long()

            # Add noise to latents (forward diffusion)
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Encode text
            text_inputs = tokenizer(
                prompts,
                padding="max_length",
                max_length=tokenizer.model_max_length,
                truncation=True,
                return_tensors="pt"
            )
            text_embeddings = text_encoder(
                text_inputs.input_ids.to(accelerator.device)
            )[0]

            # ControlNet forward pass
            # Note: ControlNet expects conditioning at FULL image resolution (512x512)
            # It has its own encoder to process the conditioning image
            down_block_res_samples, mid_block_res_sample = controlnet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=text_embeddings,
                controlnet_cond=conditioning,  # Full resolution, not resized
                return_dict=False
            )

            # U-Net forward pass with ControlNet conditioning
            noise_pred = unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=text_embeddings,
                down_block_additional_residuals=down_block_res_samples,
                mid_block_additional_residual=mid_block_res_sample
            ).sample

            # Compute loss (MSE between predicted and actual noise)
            loss = F.mse_loss(noise_pred, noise)

            accelerator.backward(loss)
            optimizer.step()
            lr_scheduler.step()  # Update learning rate
            optimizer.zero_grad()

            # Logging
            global_step += 1
            loss_history.append(loss.item())

            if global_step % LOG_STEPS == 0:
                avg_loss = np.mean(loss_history[-LOG_STEPS:])
                current_lr = lr_scheduler.get_last_lr()[0]
                progress_bar.set_postfix({
                    'loss': f'{avg_loss:.4f}',
                    'lr': f'{current_lr:.2e}',
                    'step': global_step
                })

            progress_bar.update(1)

            # Save checkpoint
            if global_step % SAVE_STEPS == 0:
                checkpoint_path = OUTPUT_DIR / f'checkpoint-{global_step}'
                accelerator.save_state(checkpoint_path)
                print(f"\nSaved checkpoint at step {global_step}")
                # Clear CUDA cache to prevent memory fragmentation crashes
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

            # Generate sample (separate from checkpoint saving)
            if global_step % SAMPLE_STEPS == 0:
                generate_sample(
                    controlnet, unet, vae, text_encoder, tokenizer,
                    noise_scheduler, accelerator.device,
                    global_step
                )

    progress_bar.close()

    # Save final model
    print()
    print("Saving final model...")
    final_path = MODEL_DIR / 'controlnet_fill50k.pt'
    torch.save(controlnet.state_dict(), final_path)
    print(f"Model saved to: {final_path}")

    # Save loss curve
    save_loss_curve(loss_history)

    print()
    print("=" * 60)
    print("Training complete!")
    print(f"Final model: {final_path}")
    print(f"Training samples: {OUTPUT_DIR}")
    print("=" * 60)

def generate_sample(controlnet, unet, vae, text_encoder, tokenizer,
                    noise_scheduler, device, step):
    """Generate a sample image during training."""
    controlnet.eval()

    # Load a sample conditioning image
    sample_path = DATASET_DIR / 'source' / '0.png'
    if not sample_path.exists():
        return

    # Load and preprocess
    source = Image.open(sample_path).convert('RGB').resize((IMAGE_SIZE, IMAGE_SIZE))
    source_tensor = torch.from_numpy(np.array(source)).float() / 127.5 - 1
    source_tensor = source_tensor.permute(2, 0, 1).unsqueeze(0).to(device)

    prompt = "a circle filled with color"

    with torch.no_grad():
        # Encode text
        text_inputs = tokenizer(
            [prompt],
            padding="max_length",
            max_length=tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt"
        )
        text_embeddings = text_encoder(text_inputs.input_ids.to(device))[0]

        # Start from noise
        latents = torch.randn((1, 4, IMAGE_SIZE // 8, IMAGE_SIZE // 8), device=device)

        # Denoising loop
        noise_scheduler.set_timesteps(50)
        for t in noise_scheduler.timesteps:
            # ControlNet conditioning (full resolution, not resized)
            down_samples, mid_sample = controlnet(
                latents,
                t.unsqueeze(0).to(device),
                encoder_hidden_states=text_embeddings,
                controlnet_cond=source_tensor,  # Full resolution
                return_dict=False
            )

            # U-Net prediction
            noise_pred = unet(
                latents,
                t.unsqueeze(0).to(device),
                encoder_hidden_states=text_embeddings,
                down_block_additional_residuals=down_samples,
                mid_block_additional_residual=mid_sample
            ).sample

            # Update latents
            latents = noise_scheduler.step(noise_pred, t, latents).prev_sample

        # Decode to image
        latents = latents / vae.config.scaling_factor
        image = vae.decode(latents).sample

        # Convert to PIL
        image = (image / 2 + 0.5).clamp(0, 1)
        image = (image[0].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        image = Image.fromarray(image)

        # Save
        sample_path = OUTPUT_DIR / f'sample-{step}.png'
        image.save(sample_path)
        print(f"Sample saved: {sample_path}")

    controlnet.train()

def save_loss_curve(loss_history):
    """Save training loss curve visualization."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    # Smooth the loss with moving average
    window = min(100, len(loss_history) // 10)
    if window > 1:
        smoothed = np.convolve(loss_history, np.ones(window)/window, mode='valid')
        ax.plot(smoothed, color='blue', label='Smoothed Loss')
    else:
        ax.plot(loss_history, color='blue', alpha=0.7, label='Training Loss')

    ax.set_xlabel('Training Steps', fontsize=12)
    ax.set_ylabel('MSE Loss', fontsize=12)
    ax.set_title('ControlNet Training Loss (Fill50K)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'loss_curve.png', bbox_inches='tight', dpi=150)
    plt.close()

    print(f"Loss curve saved: {OUTPUT_DIR / 'loss_curve.png'}")

def main():
    global MAX_TRAIN_STEPS, MAX_SAMPLES, RESUME_CHECKPOINT  # Allow overriding via args

    parser = argparse.ArgumentParser(description='Exercise 3A: Train ControlNet on Fill50K')
    parser.add_argument('--verify', action='store_true', help='Verify dataset only')
    parser.add_argument('--train', action='store_true', help='Start training')
    parser.add_argument('--resume', type=int, default=None, help='Resume from checkpoint step')
    parser.add_argument('--steps', type=int, default=MAX_TRAIN_STEPS, help='Max training steps')
    parser.add_argument('--samples', type=int, default=None, help='Number of samples to use (default: all)')

    args = parser.parse_args()

    if args.steps != MAX_TRAIN_STEPS:
        MAX_TRAIN_STEPS = args.steps
    if args.samples is not None:
        MAX_SAMPLES = args.samples
    if args.resume is not None:
        RESUME_CHECKPOINT = args.resume

    if args.verify:
        verify_dataset()
    elif args.train:
        train_controlnet()
    else:
        print("ControlNet Training (Fill50K) - Extended Training Version")
        print()
        print("Usage:")
        print("  python exercise3a_train_controlnet.py --verify         # Check dataset")
        print("  python exercise3a_train_controlnet.py --train          # Start fresh training")
        print("  python exercise3a_train_controlnet.py --train --resume 2000  # Resume from step 2000")
        print()
        print("Options:")
        print(f"  --steps N     Max training steps (default: {MAX_TRAIN_STEPS})")
        print(f"  --samples N   Dataset samples to use (default: all 50,000)")
        print(f"  --resume N    Resume from checkpoint at step N")
        print()
        print("Recommended for Extended Training (24 hours):")
        print("  python exercise3a_train_controlnet.py --train --resume 2000 --steps 10000")
        print()
        print("Requirements:")
        print("  - GPU with 8GB+ VRAM")
        print("  - Fill50K dataset (run download_fill50k.py)")
        print("  - Estimated time: ~20-24 hours for 10,000 steps")

if __name__ == '__main__':
    main()
