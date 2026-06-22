import os
import sys
from pathlib import Path
import argparse
import math
from datetime import datetime

# Add module directory to path
MODULE_DIR = Path(__file__).parent
sys.path.insert(0, str(MODULE_DIR))

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm

# Hugging Face imports
try:
    from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel
    from diffusers.optimization import get_scheduler
    from transformers import CLIPTextModel, CLIPTokenizer
    from accelerate import Accelerator
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("\nPlease install required packages:")
    print("  pip install diffusers transformers accelerate")
    sys.exit(1)

from dreambooth_utils import (
    print_section_header,
    get_device,
    check_gpu_memory,
    create_image_grid,
    MODELS_DIR,
    OUTPUTS_DIR,
    TRAINING_IMAGES_DIR
)

# =============================================================================
# Configuration
# =============================================================================

# Model settings
PRETRAINED_MODEL = "runwayml/stable-diffusion-v1-5"

# Token settings
PLACEHOLDER_TOKEN = "<african-fabric>"  # The new token to learn
INITIALIZER_TOKEN = "pattern"            # Initialize from this existing token

# Training settings
LEARNING_RATE = 5e-4
MAX_TRAIN_STEPS = 3000        # Total training steps
TRAIN_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
MIXED_PRECISION = "fp16"      # Use fp16 for faster training

# Logging and checkpoints
LOG_INTERVAL = 100            # Log every N steps
SAMPLE_INTERVAL = 500         # Generate samples every N steps
SAVE_INTERVAL = 1000          # Save checkpoint every N steps

# Output paths
OUTPUT_DIR = MODELS_DIR / "fabric_textual_inversion"
PROGRESS_DIR = MODULE_DIR / "training_progress_ti"

# =============================================================================
# Dataset
# =============================================================================

class TextualInversionDataset(Dataset):
    """
    Dataset for Textual Inversion training.

    Each training image is paired with a text prompt containing the
    placeholder token. The model learns to associate the token embedding
    with the visual features in these images.
    """

    def __init__(
        self,
        data_root,
        tokenizer,
        placeholder_token,
        size=512,
        repeats=100,
        flip_p=0.5,
        center_crop=True
    ):
        self.data_root = Path(data_root)
        self.tokenizer = tokenizer
        self.placeholder_token = placeholder_token
        self.size = size
        self.flip_p = flip_p
        self.center_crop = center_crop

        # Find all images
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
        self.image_paths = []
        for ext in extensions:
            self.image_paths.extend(self.data_root.glob(ext))
            self.image_paths.extend(self.data_root.glob(ext.upper()))

        if not self.image_paths:
            raise ValueError(f"No images found in {data_root}")

        print(f"Found {len(self.image_paths)} training images")

        # Repeat dataset to reach desired training length
        self._length = len(self.image_paths) * repeats

        # Template prompts for training
        self.templates = [
            f"a photo of {placeholder_token}",
            f"a rendering of {placeholder_token}",
            f"a cropped photo of {placeholder_token}",
            f"the photo of {placeholder_token}",
            f"a photo of a clean {placeholder_token}",
            f"a photo of a dirty {placeholder_token}",
            f"a dark photo of {placeholder_token}",
            f"a photo of my {placeholder_token}",
            f"a photo of the cool {placeholder_token}",
            f"a close-up photo of {placeholder_token}",
            f"a bright photo of {placeholder_token}",
            f"a photo of a nice {placeholder_token}",
            f"a photo of a weird {placeholder_token}",
            f"a blurry photo of {placeholder_token}",
            f"a good photo of {placeholder_token}",
        ]

    def __len__(self):
        return self._length

    def __getitem__(self, idx):
        # Select image (with wrapping)
        image_idx = idx % len(self.image_paths)
        image_path = self.image_paths[image_idx]

        # Load and preprocess image
        image = Image.open(image_path).convert("RGB")

        # Center crop to square
        if self.center_crop:
            min_dim = min(image.size)
            left = (image.width - min_dim) // 2
            top = (image.height - min_dim) // 2
            image = image.crop((left, top, left + min_dim, top + min_dim))

        # Resize
        image = image.resize((self.size, self.size), Image.Resampling.LANCZOS)

        # Random horizontal flip
        if torch.rand(1).item() < self.flip_p:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        # Convert to tensor and normalize to [-1, 1]
        image = np.array(image).astype(np.float32) / 255.0
        image = image * 2.0 - 1.0
        image = torch.from_numpy(image).permute(2, 0, 1)

        # Select random template prompt
        template_idx = idx % len(self.templates)
        text = self.templates[template_idx]

        return {"pixel_values": image, "text": text}

# =============================================================================
# Training Functions
# =============================================================================

def save_progress_samples(pipeline, placeholder_token, step, device, output_dir):
    """Generate and save sample images during training."""
    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)

    prompts = [
        f"a photo of {placeholder_token}",
        f"a beautiful {placeholder_token} with vibrant colors",
        f"{placeholder_token} in watercolor style",
        f"a detailed close-up of {placeholder_token}",
    ]

    images = []
    with torch.no_grad():
        for prompt in prompts:
            image = pipeline(
                prompt,
                num_inference_steps=30,
                guidance_scale=7.5,
                generator=torch.Generator(device=device).manual_seed(42)
            ).images[0]
            images.append(image)

    # Create grid
    grid = create_image_grid(images, rows=2, cols=2, padding=4)
    output_path = output_dir / f"step_{step:05d}.png"
    grid.save(output_path)
    print(f"  Saved samples to: {output_path}")

    return grid

def train_textual_inversion():
    """Main training function for Textual Inversion."""

    print_section_header("Exercise 3a: Train Textual Inversion")

    # Setup accelerator for distributed training / mixed precision
    accelerator = Accelerator(
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        mixed_precision=MIXED_PRECISION,
    )

    device = accelerator.device
    print(f"\nDevice: {device}")

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load tokenizer and add placeholder token
    print("\n" + "=" * 50)
    print("Step 1: Setting Up Tokenizer")
    print("=" * 50)

    tokenizer = CLIPTokenizer.from_pretrained(
        PRETRAINED_MODEL,
        subfolder="tokenizer"
    )

    # Add the placeholder token
    num_added_tokens = tokenizer.add_tokens(PLACEHOLDER_TOKEN)
    if num_added_tokens == 0:
        raise ValueError(f"Token {PLACEHOLDER_TOKEN} already exists in tokenizer")

    print(f"Added placeholder token: {PLACEHOLDER_TOKEN}")
    placeholder_token_id = tokenizer.convert_tokens_to_ids(PLACEHOLDER_TOKEN)
    print(f"Token ID: {placeholder_token_id}")

    # Get the ID of the initializer token
    initializer_token_id = tokenizer.encode(INITIALIZER_TOKEN, add_special_tokens=False)[0]
    print(f"Initializer token '{INITIALIZER_TOKEN}' ID: {initializer_token_id}")

    # Step 2: Load text encoder and resize embedding
    print("\n" + "=" * 50)
    print("Step 2: Loading Text Encoder")
    print("=" * 50)

    text_encoder = CLIPTextModel.from_pretrained(
        PRETRAINED_MODEL,
        subfolder="text_encoder"
    )

    # Resize token embeddings to include our new token
    text_encoder.resize_token_embeddings(len(tokenizer))

    # Initialize the new token embedding with the initializer token
    token_embeds = text_encoder.get_input_embeddings().weight.data
    token_embeds[placeholder_token_id] = token_embeds[initializer_token_id].clone()

    print(f"Token embedding initialized from '{INITIALIZER_TOKEN}'")
    print(f"Embedding dimension: {token_embeds[placeholder_token_id].shape}")

    # Step 3: Load other model components (frozen)
    print("\n" + "=" * 50)
    print("Step 3: Loading Model Components (Frozen)")
    print("=" * 50)

    vae = AutoencoderKL.from_pretrained(PRETRAINED_MODEL, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(PRETRAINED_MODEL, subfolder="unet")
    noise_scheduler = DDPMScheduler.from_pretrained(PRETRAINED_MODEL, subfolder="scheduler")

    # Freeze everything except the new embedding
    vae.requires_grad_(False)
    unet.requires_grad_(False)
    text_encoder.requires_grad_(False)

    # Only the new token embedding is trainable
    text_encoder.text_model.embeddings.token_embedding.requires_grad_(True)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in text_encoder.parameters() if p.requires_grad)
    print(f"Trainable parameters: {trainable_params:,}")
    print("(This is ONLY the new token embedding - entire model is frozen)")

    # Step 4: Setup dataset and dataloader
    print("\n" + "=" * 50)
    print("Step 4: Loading Training Data")
    print("=" * 50)

    if not TRAINING_IMAGES_DIR.exists() or not any(TRAINING_IMAGES_DIR.iterdir()):
        print(f"\nError: No training images found in {TRAINING_IMAGES_DIR}")
        print("\nTo continue, please:")
        print("1. Copy 10 fabric images from the African fabric dataset:")
        print("   Source: Module_12/.../12.1.2_dcgan_art/african_fabric_dataset/")
        print(f"   Destination: {TRAINING_IMAGES_DIR}/")
        print("\n2. Re-run this script")
        return

    dataset = TextualInversionDataset(
        data_root=TRAINING_IMAGES_DIR,
        tokenizer=tokenizer,
        placeholder_token=PLACEHOLDER_TOKEN,
        size=512,
        repeats=100
    )

    dataloader = DataLoader(
        dataset,
        batch_size=TRAIN_BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    # Step 5: Setup optimizer
    print("\n" + "=" * 50)
    print("Step 5: Setting Up Optimizer")
    print("=" * 50)

    # Only optimize the token embedding
    optimizer = torch.optim.AdamW(
        text_encoder.get_input_embeddings().parameters(),
        lr=LEARNING_RATE,
        betas=(0.9, 0.999),
        weight_decay=1e-2,
        eps=1e-8
    )

    # Learning rate scheduler
    lr_scheduler = get_scheduler(
        "constant",
        optimizer=optimizer,
        num_warmup_steps=0,
        num_training_steps=MAX_TRAIN_STEPS
    )

    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Max training steps: {MAX_TRAIN_STEPS}")

    # Step 6: Prepare for training with accelerator
    text_encoder, optimizer, dataloader, lr_scheduler = accelerator.prepare(
        text_encoder, optimizer, dataloader, lr_scheduler
    )

    vae.to(device)
    unet.to(device)

    # Step 7: Training loop
    print("\n" + "=" * 50)
    print("Step 6: Training")
    print("=" * 50)

    # Keep a copy of the original embeddings to prevent other tokens from changing
    orig_embeds_params = text_encoder.get_input_embeddings().weight.data.clone()

    global_step = 0
    losses = []

    progress_bar = tqdm(total=MAX_TRAIN_STEPS, desc="Training")

    while global_step < MAX_TRAIN_STEPS:
        for batch in dataloader:
            with accelerator.accumulate(text_encoder):
                # Convert images to latent space
                latents = vae.encode(batch["pixel_values"].to(device)).latent_dist.sample()
                latents = latents * vae.config.scaling_factor

                # Sample noise (same as DDPM training!)
                noise = torch.randn_like(latents)

                # Sample random timesteps
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps,
                    (latents.shape[0],), device=device
                ).long()

                # Add noise to latents (forward diffusion - same as Module 12.3.1!)
                noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

                # Get text embeddings
                input_ids = tokenizer(
                    batch["text"],
                    padding="max_length",
                    truncation=True,
                    max_length=tokenizer.model_max_length,
                    return_tensors="pt"
                ).input_ids.to(device)

                encoder_hidden_states = text_encoder(input_ids)[0]

                # Predict noise (same objective as DDPM!)
                noise_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

                # Calculate loss (MSE between predicted and actual noise)
                loss = F.mse_loss(noise_pred.float(), noise.float(), reduction="mean")

                # Backpropagate
                accelerator.backward(loss)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

                # Keep all embeddings except our new one frozen
                index_grads_to_zero = torch.arange(len(tokenizer)) != placeholder_token_id
                with torch.no_grad():
                    accelerator.unwrap_model(text_encoder).get_input_embeddings().weight[
                        index_grads_to_zero
                    ] = orig_embeds_params[index_grads_to_zero]

            # Logging
            losses.append(loss.item())

            if global_step % LOG_INTERVAL == 0:
                avg_loss = np.mean(losses[-LOG_INTERVAL:])
                progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})

            # Save samples
            if global_step > 0 and global_step % SAMPLE_INTERVAL == 0:
                print(f"\n  Generating samples at step {global_step}...")

                # Create inference pipeline
                pipeline = StableDiffusionPipeline.from_pretrained(
                    PRETRAINED_MODEL,
                    text_encoder=accelerator.unwrap_model(text_encoder),
                    tokenizer=tokenizer,
                    vae=vae,
                    unet=unet,
                    safety_checker=None,
                    requires_safety_checker=False,
                    torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
                )

                save_progress_samples(pipeline, PLACEHOLDER_TOKEN, global_step, device, PROGRESS_DIR)
                del pipeline
                torch.cuda.empty_cache() if device.type == "cuda" else None

            # Save checkpoint
            if global_step > 0 and global_step % SAVE_INTERVAL == 0:
                print(f"\n  Saving checkpoint at step {global_step}...")
                save_path = OUTPUT_DIR / f"learned_embeds_step_{global_step}.safetensors"
                save_embedding(accelerator.unwrap_model(text_encoder), placeholder_token_id, save_path)

            global_step += 1
            progress_bar.update(1)

            if global_step >= MAX_TRAIN_STEPS:
                break

    progress_bar.close()

    # Step 8: Save final embedding
    print("\n" + "=" * 50)
    print("Step 7: Saving Final Embedding")
    print("=" * 50)

    final_path = OUTPUT_DIR / "learned_embeds.safetensors"
    save_embedding(accelerator.unwrap_model(text_encoder), placeholder_token_id, final_path)

    # Save loss curve
    plt.figure(figsize=(10, 5))
    plt.plot(losses)
    plt.xlabel("Training Step")
    plt.ylabel("Loss")
    plt.title("Textual Inversion Training Loss")
    plt.grid(True, alpha=0.3)
    plt.savefig(OUTPUTS_DIR / "exercise3a_loss_curve.png", dpi=150)
    plt.close()
    print(f"Saved loss curve to: {OUTPUTS_DIR / 'exercise3a_loss_curve.png'}")

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"""
Output files:
- Embedding: {final_path}
- Progress samples: {PROGRESS_DIR}/
- Loss curve: {OUTPUTS_DIR / 'exercise3a_loss_curve.png'}

File size: {final_path.stat().st_size / 1024:.1f} KB
(Compare to LoRA: 10-50 MB, Full fine-tune: ~5 GB)

To use your trained embedding:
    from diffusers import StableDiffusionPipeline

    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    pipe.load_textual_inversion("{final_path}", token="{PLACEHOLDER_TOKEN}")

    image = pipe("a beautiful {PLACEHOLDER_TOKEN}").images[0]
    """)

def save_embedding(text_encoder, token_id, save_path):
    """Save the learned embedding to a safetensors file."""
    from safetensors.torch import save_file

    embedding = text_encoder.get_input_embeddings().weight[token_id].detach().cpu()
    state_dict = {PLACEHOLDER_TOKEN: embedding}
    save_file(state_dict, save_path)
    print(f"Saved embedding to: {save_path}")

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Textual Inversion")
    parser.add_argument("--max_steps", type=int, default=MAX_TRAIN_STEPS,
                        help="Maximum training steps")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE,
                        help="Learning rate")
    args = parser.parse_args()

    # Update config from args
    MAX_TRAIN_STEPS = args.max_steps
    LEARNING_RATE = args.lr

    train_textual_inversion()
