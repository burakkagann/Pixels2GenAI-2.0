import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image
from pathlib import Path
import argparse
from tqdm import tqdm

# Script configuration
SCRIPT_DIR = Path(__file__).parent
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# LoRA hyperparameters (based on HuggingFace official recommendations)
LORA_RANK = 4  # Low rank for efficient adaptation
LORA_ALPHA = 4  # Scaling factor
BATCH_SIZE = 1  # Small batches for limited GPU memory
LEARNING_RATE = 1e-4
MAX_TRAIN_STEPS = 15000  # Max steps (not epochs) - prevents overfitting
LR_WARMUP_STEPS = 500  # Gradual warmup for stable training
IMAGE_SIZE = 512
SAVE_STEPS = 1000  # Save checkpoints every 1000 steps
SAMPLE_STEPS = 3000  # Generate samples every 3000 steps

# Paths
FABRIC_DIR = SCRIPT_DIR.parent.parent / '12.1_generative_adversarial_networks' / '12.1.2_dcgan_art' / 'african_fabric_processed'
OUTPUT_DIR = SCRIPT_DIR / 'training_results' / 'lora_fabrics'
MODEL_DIR = SCRIPT_DIR / 'models'

class AfricanFabricDataset(Dataset):
    """
    African Fabric Dataset for LoRA training.

    Uses the preprocessed fabric images from Module 12.1.2 (DCGAN).
    Each image is paired with a generic prompt describing African textiles.
    """

    def __init__(self, data_dir, image_size=512, max_samples=None):
        self.data_dir = Path(data_dir)
        self.image_size = image_size

        if not self.data_dir.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self.data_dir}\n"
                "Please ensure Module 12.1.2 preprocessing is complete."
            )

        # Get all image files
        self.image_paths = sorted(
            list(self.data_dir.glob('*.png')) +
            list(self.data_dir.glob('*.jpg'))
        )

        if max_samples:
            self.image_paths = self.image_paths[:max_samples]

        # Generic prompts for African textiles
        self.prompts = [
            "African textile pattern with geometric designs",
            "Traditional African fabric with vibrant colors",
            "Kente cloth inspired pattern",
            "African wax print textile design",
            "Colorful African fabric pattern"
        ]

        print(f"Loaded {len(self.image_paths)} fabric images")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        # Load image
        image = Image.open(self.image_paths[idx]).convert('RGB')
        image = image.resize((self.image_size, self.image_size), Image.LANCZOS)

        # Convert to tensor (normalize to [-1, 1])
        image_tensor = torch.from_numpy(np.array(image)).float() / 127.5 - 1
        image_tensor = image_tensor.permute(2, 0, 1)  # HWC -> CHW

        # Select a random prompt
        prompt = self.prompts[idx % len(self.prompts)]

        return {
            'image': image_tensor,
            'prompt': prompt
        }

def verify_dataset():
    """Verify the African fabric dataset exists."""
    global FABRIC_DIR  # Must declare global at function start
    print("Verifying African fabric dataset...")

    if not FABRIC_DIR.exists():
        # Try alternative paths
        alt_paths = [
            SCRIPT_DIR.parent.parent / '12.1_generative_adversarial_networks' / '12.1.2_dcgan_art' / 'african_fabric_dataset',
        ]

        for alt in alt_paths:
            if alt.exists():
                FABRIC_DIR = alt
                break
        else:
            print(f"Dataset not found at: {FABRIC_DIR}")
            print()
            print("Please ensure the African fabric dataset exists from Module 12.1.2")
            return False

    # Count images
    image_count = len(list(FABRIC_DIR.glob('*.png'))) + len(list(FABRIC_DIR.glob('*.jpg')))

    if image_count == 0:
        print("No images found in dataset directory")
        return False

    print(f"Found {image_count} fabric images")
    print()
    print("Dataset verification: PASSED")
    return True

def train_lora():
    """
    Train LoRA adapter on African fabric dataset.

    LoRA adds trainable low-rank decomposition matrices to frozen
    pretrained weights. This enables efficient fine-tuning with:
    - Much fewer trainable parameters
    - Smaller memory footprint
    - Faster training convergence
    """
    print("=" * 60)
    print("LoRA Training on African Fabrics")
    print("=" * 60)
    print()

    # Verify dataset
    if not verify_dataset():
        return

    print(f"Device: {DEVICE}")
    print(f"LoRA rank: {LORA_RANK}")
    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Max training steps: {MAX_TRAIN_STEPS}")
    print(f"LR warmup steps: {LR_WARMUP_STEPS}")
    print(f"LR scheduler: cosine")
    print()

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Import training libraries
    try:
        from diffusers import StableDiffusionPipeline, DDPMScheduler
        from peft import LoraConfig, get_peft_model
        from transformers import get_cosine_schedule_with_warmup
    except ImportError as e:
        print("Required libraries not found.")
        print("Please install:")
        print("  pip install diffusers transformers accelerate peft")
        print(f"Error: {e}")
        return

    print("Loading pretrained Stable Diffusion...")

    # Load pipeline
    pipeline = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
        safety_checker=None
    )

    # Get components
    vae = pipeline.vae
    text_encoder = pipeline.text_encoder
    tokenizer = pipeline.tokenizer
    unet = pipeline.unet
    noise_scheduler = DDPMScheduler.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        subfolder="scheduler"
    )

    # Freeze VAE and text encoder
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)

    # Configure LoRA for U-Net
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],  # Attention layers
        lora_dropout=0.1,
    )

    # Apply LoRA to U-Net
    unet = get_peft_model(unet, lora_config)
    unet.print_trainable_parameters()

    # Move to device
    vae.to(DEVICE)
    text_encoder.to(DEVICE)
    unet.to(DEVICE)

    # Create dataset and dataloader
    dataset = AfricanFabricDataset(FABRIC_DIR, image_size=IMAGE_SIZE)
    dataloader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    # Optimizer
    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.01
    )

    # Learning rate scheduler (cosine with warmup)
    lr_scheduler = get_cosine_schedule_with_warmup(
        optimizer=optimizer,
        num_warmup_steps=LR_WARMUP_STEPS,
        num_training_steps=MAX_TRAIN_STEPS
    )

    # Training loop (step-based, not epoch-based)
    global_step = 0
    loss_history = []

    print()
    print("Starting LoRA training...")
    print(f"Training for {MAX_TRAIN_STEPS} steps with cosine LR schedule")
    print("-" * 60)

    progress_bar = tqdm(total=MAX_TRAIN_STEPS, desc="Training LoRA")

    while global_step < MAX_TRAIN_STEPS:
        for batch in dataloader:
            if global_step >= MAX_TRAIN_STEPS:
                break

            # Get batch data
            images = batch['image'].to(DEVICE)
            prompts = batch['prompt']

            # Encode images to latent space
            with torch.no_grad():
                if DEVICE == 'cuda':
                    with torch.cuda.amp.autocast():
                        latents = vae.encode(images.half()).latent_dist.sample()
                else:
                    latents = vae.encode(images).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

            # Sample noise
            noise = torch.randn_like(latents)

            # Sample timesteps
            batch_size = latents.shape[0]
            timesteps = torch.randint(
                0, noise_scheduler.config.num_train_timesteps,
                (batch_size,), device=DEVICE
            ).long()

            # Add noise to latents
            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Encode text
            text_inputs = tokenizer(
                prompts,
                padding="max_length",
                max_length=tokenizer.model_max_length,
                truncation=True,
                return_tensors="pt"
            )
            with torch.no_grad():
                text_embeddings = text_encoder(
                    text_inputs.input_ids.to(DEVICE)
                )[0]

            # U-Net forward pass (with LoRA)
            if DEVICE == 'cuda':
                with torch.cuda.amp.autocast():
                    noise_pred = unet(
                        noisy_latents,
                        timesteps,
                        encoder_hidden_states=text_embeddings
                    ).sample
                    loss = F.mse_loss(noise_pred.float(), noise.float())
            else:
                noise_pred = unet(
                    noisy_latents,
                    timesteps,
                    encoder_hidden_states=text_embeddings
                ).sample
                loss = F.mse_loss(noise_pred, noise)

            # Backward pass
            loss.backward()
            optimizer.step()
            lr_scheduler.step()  # Update learning rate
            optimizer.zero_grad()

            # Logging
            global_step += 1
            loss_history.append(loss.item())

            # Update progress bar
            current_lr = lr_scheduler.get_last_lr()[0]
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'lr': f'{current_lr:.2e}'
            })
            progress_bar.update(1)

            # Save checkpoint
            if global_step % SAVE_STEPS == 0:
                save_lora_checkpoint(unet, global_step)

            # Generate sample periodically
            if global_step % SAMPLE_STEPS == 0:
                generate_sample(pipeline, unet, global_step)

    progress_bar.close()

    # Save final model
    print()
    print("Saving final LoRA adapter...")
    save_lora_checkpoint(unet, global_step, final=True)

    # Save loss curve
    save_loss_curve(loss_history)

    print()
    print("=" * 60)
    print("LoRA Training Complete!")
    print(f"Adapter saved: {MODEL_DIR / 'lora_african_fabrics.safetensors'}")
    print(f"Training samples: {OUTPUT_DIR}")
    print("=" * 60)

def save_lora_checkpoint(unet, step, final=False):
    """Save LoRA adapter weights."""
    if final:
        output_path = MODEL_DIR / 'lora_african_fabrics.safetensors'
    else:
        output_path = OUTPUT_DIR / f'lora_checkpoint_{step}.pt'

    # Get LoRA state dict
    lora_state_dict = {}
    for name, param in unet.named_parameters():
        if 'lora' in name.lower() and param.requires_grad:
            lora_state_dict[name] = param.data.cpu()

    torch.save(lora_state_dict, output_path)
    print(f"LoRA checkpoint saved: {output_path}")

def generate_sample(pipeline, unet, step):
    """Generate a sample image during training."""
    unet.eval()

    prompt = "African textile pattern with geometric designs, vibrant colors"

    with torch.no_grad():
        generator = torch.Generator(device=DEVICE).manual_seed(42)

        # Create temporary pipeline with LoRA U-Net
        # Note: This is simplified; full implementation would load LoRA properly
        image = pipeline(
            prompt=prompt,
            num_inference_steps=25,
            generator=generator
        ).images[0]

        sample_path = OUTPUT_DIR / f'sample_step_{step}.png'
        image.save(sample_path)
        print(f"\nSample saved: {sample_path}")

    unet.train()

def save_loss_curve(loss_history):
    """Save training loss curve."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    # Smooth the loss
    window = min(50, len(loss_history) // 10)
    if window > 1:
        smoothed = np.convolve(loss_history, np.ones(window)/window, mode='valid')
        ax.plot(smoothed, color='green', label='Smoothed Loss')
    else:
        ax.plot(loss_history, color='green', alpha=0.7, label='Training Loss')

    ax.set_xlabel('Training Steps', fontsize=12)
    ax.set_ylabel('MSE Loss', fontsize=12)
    ax.set_title('LoRA Training Loss (African Fabrics)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'lora_loss_curve.png', bbox_inches='tight', dpi=150)
    plt.close()

    print(f"Loss curve saved: {OUTPUT_DIR / 'lora_loss_curve.png'}")

def main():
    global MAX_TRAIN_STEPS, LORA_RANK  # Must declare global at function start

    parser = argparse.ArgumentParser(description='Exercise 3B: Train LoRA on African Fabrics')
    parser.add_argument('--verify', action='store_true', help='Verify dataset only')
    parser.add_argument('--train', action='store_true', help='Start training')
    parser.add_argument('--steps', type=int, default=MAX_TRAIN_STEPS, help='Max training steps')
    parser.add_argument('--rank', type=int, default=LORA_RANK, help='LoRA rank')

    args = parser.parse_args()

    if args.steps != MAX_TRAIN_STEPS:
        MAX_TRAIN_STEPS = args.steps

    if args.rank != LORA_RANK:
        LORA_RANK = args.rank

    if args.verify:
        verify_dataset()
    elif args.train:
        train_lora()
    else:
        print("LoRA Training (African Fabrics)")
        print()
        print("Usage:")
        print("  python exercise3b_train_lora.py --verify  # Check dataset")
        print("  python exercise3b_train_lora.py --train   # Start training")
        print()
        print("Options:")
        print("  --steps N    Set max training steps (default: 15000)")
        print("  --rank N     Set LoRA rank (default: 4)")
        print()
        print("Requirements:")
        print("  - GPU with 6GB+ VRAM")
        print("  - African fabric dataset from Module 12.1.2")
        print("  - 45-90 minutes training time")

if __name__ == '__main__':
    main()
