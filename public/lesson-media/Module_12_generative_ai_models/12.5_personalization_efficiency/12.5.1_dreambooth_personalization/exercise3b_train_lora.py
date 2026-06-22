import os
import sys
from pathlib import Path
import argparse
import math
from datetime import datetime
import random

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
    from diffusers import (
        AutoencoderKL,
        DDPMScheduler,
        StableDiffusionPipeline,
        UNet2DConditionModel,
        DPMSolverMultistepScheduler
    )
    from diffusers.optimization import get_scheduler
    from diffusers.loaders import LoraLoaderMixin
    from transformers import CLIPTextModel, CLIPTokenizer
    from accelerate import Accelerator
    from peft import LoraConfig, get_peft_model
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("\nPlease install required packages:")
    print("  pip install diffusers transformers accelerate peft")
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

# Subject and class settings
INSTANCE_PROMPT = "a sks african fabric pattern"     # Prompt for YOUR subject
CLASS_PROMPT = "a fabric pattern"                     # Prompt for generic class
NUM_CLASS_IMAGES = 100                                # Class images for prior preservation

# LoRA settings
LORA_RANK = 4               # Lower = smaller file, less expressive; Higher = more capacity
LORA_ALPHA = 32             # Scaling factor for LoRA updates
LORA_DROPOUT = 0.0          # Dropout for regularization

# Training settings
LEARNING_RATE = 1e-4        # LoRA uses higher LR than full fine-tune
MAX_TRAIN_STEPS = 800       # Total training steps
TRAIN_BATCH_SIZE = 1
GRADIENT_ACCUMULATION_STEPS = 4
MIXED_PRECISION = "fp16"
PRIOR_LOSS_WEIGHT = 1.0     # Weight for prior preservation loss

# Logging and checkpoints
LOG_INTERVAL = 50
SAMPLE_INTERVAL = 100
SAVE_INTERVAL = 200

# Output paths
OUTPUT_DIR = MODELS_DIR / "fabric_lora"
PROGRESS_DIR = MODULE_DIR / "training_progress_lora"
CLASS_IMAGES_DIR = MODULE_DIR / "class_images"

# =============================================================================
# Dataset
# =============================================================================

class DreamBoothDataset(Dataset):
    """
    Dataset for DreamBooth training with prior preservation.

    This dataset alternates between:
    1. Instance images (your subject) with instance_prompt
    2. Class images (generic examples) with class_prompt

    The ratio ensures both types contribute equally to training.
    """

    def __init__(
        self,
        instance_data_root,
        class_data_root,
        tokenizer,
        instance_prompt,
        class_prompt,
        size=512,
        center_crop=True
    ):
        self.tokenizer = tokenizer
        self.instance_prompt = instance_prompt
        self.class_prompt = class_prompt
        self.size = size
        self.center_crop = center_crop

        # Load instance images (your subject)
        self.instance_images = self._load_images(instance_data_root)
        print(f"Loaded {len(self.instance_images)} instance images")

        # Load class images (for prior preservation)
        self.class_images = self._load_images(class_data_root)
        print(f"Loaded {len(self.class_images)} class images")

        self._length = max(len(self.instance_images), len(self.class_images))

    def _load_images(self, data_root):
        """Load all images from a directory."""
        data_root = Path(data_root)
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.webp']
        images = []
        for ext in extensions:
            images.extend(data_root.glob(ext))
            images.extend(data_root.glob(ext.upper()))
        return sorted(images)

    def _preprocess_image(self, image_path):
        """Load and preprocess a single image."""
        image = Image.open(image_path).convert("RGB")

        # Center crop to square
        if self.center_crop:
            min_dim = min(image.size)
            left = (image.width - min_dim) // 2
            top = (image.height - min_dim) // 2
            image = image.crop((left, top, left + min_dim, top + min_dim))

        # Resize
        image = image.resize((self.size, self.size), Image.Resampling.LANCZOS)

        # Convert to tensor and normalize to [-1, 1]
        image = np.array(image).astype(np.float32) / 255.0
        image = image * 2.0 - 1.0
        image = torch.from_numpy(image).permute(2, 0, 1)

        return image

    def __len__(self):
        return self._length

    def __getitem__(self, idx):
        example = {}

        # Instance image and prompt
        instance_idx = idx % len(self.instance_images)
        example["instance_images"] = self._preprocess_image(self.instance_images[instance_idx])
        example["instance_prompt_ids"] = self.tokenizer(
            self.instance_prompt,
            padding="max_length",
            truncation=True,
            max_length=self.tokenizer.model_max_length,
            return_tensors="pt"
        ).input_ids[0]

        # Class image and prompt (for prior preservation)
        if self.class_images:
            class_idx = idx % len(self.class_images)
            example["class_images"] = self._preprocess_image(self.class_images[class_idx])
            example["class_prompt_ids"] = self.tokenizer(
                self.class_prompt,
                padding="max_length",
                truncation=True,
                max_length=self.tokenizer.model_max_length,
                return_tensors="pt"
            ).input_ids[0]

        return example

# =============================================================================
# Helper Functions
# =============================================================================

def generate_class_images(pipe, class_prompt, num_images, output_dir, device):
    """
    Generate class images for prior preservation.

    These images represent the general "class" (e.g., generic fabric patterns)
    that we want the model to remember how to generate.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing = list(output_dir.glob("*.png"))
    if len(existing) >= num_images:
        print(f"Class images already exist: {len(existing)} images")
        return

    print(f"Generating {num_images} class images for prior preservation...")
    print(f"Prompt: '{class_prompt}'")

    pipe.to(device)
    pipe.set_progress_bar_config(disable=True)

    for i in tqdm(range(num_images)):
        with torch.no_grad():
            image = pipe(
                class_prompt,
                num_inference_steps=30,
                guidance_scale=7.5,
                generator=torch.Generator(device=device).manual_seed(i)
            ).images[0]

        image.save(output_dir / f"class_{i:04d}.png")

    print(f"Generated {num_images} class images to: {output_dir}")

def save_progress_samples(unet, text_encoder, vae, tokenizer, step, device, output_dir):
    """Generate and save sample images during training."""

    # Create pipeline with current weights
    pipeline = StableDiffusionPipeline.from_pretrained(
        PRETRAINED_MODEL,
        unet=unet,
        text_encoder=text_encoder,
        vae=vae,
        tokenizer=tokenizer,
        safety_checker=None,
        requires_safety_checker=False,
        torch_dtype=torch.float16 if device.type == "cuda" else torch.float32
    )
    pipeline.to(device)
    pipeline.set_progress_bar_config(disable=True)

    prompts = [
        INSTANCE_PROMPT,
        f"a beautiful {INSTANCE_PROMPT}, detailed texture",
        f"{INSTANCE_PROMPT} in watercolor style",
        f"a dress made of sks african fabric",
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

    del pipeline
    torch.cuda.empty_cache() if device.type == "cuda" else None

    return grid

# =============================================================================
# Main Training Function
# =============================================================================

def train_dreambooth_lora():
    """Main training function for DreamBooth with LoRA."""

    print_section_header("Exercise 3b: Train DreamBooth with LoRA")

    # Setup accelerator
    accelerator = Accelerator(
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        mixed_precision=MIXED_PRECISION,
    )

    device = accelerator.device
    print(f"\nDevice: {device}")
    if device.type == "cuda":
        check_gpu_memory()

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    CLASS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load model components
    print("\n" + "=" * 50)
    print("Step 1: Loading Model Components")
    print("=" * 50)

    tokenizer = CLIPTokenizer.from_pretrained(PRETRAINED_MODEL, subfolder="tokenizer")
    text_encoder = CLIPTextModel.from_pretrained(PRETRAINED_MODEL, subfolder="text_encoder")
    vae = AutoencoderKL.from_pretrained(PRETRAINED_MODEL, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(PRETRAINED_MODEL, subfolder="unet")
    noise_scheduler = DDPMScheduler.from_pretrained(PRETRAINED_MODEL, subfolder="scheduler")

    print("Loaded all model components")

    # Step 2: Generate class images for prior preservation
    print("\n" + "=" * 50)
    print("Step 2: Generating Class Images (Prior Preservation)")
    print("=" * 50)

    # Create temporary pipeline for class image generation
    temp_pipe = StableDiffusionPipeline.from_pretrained(
        PRETRAINED_MODEL,
        torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    generate_class_images(temp_pipe, CLASS_PROMPT, NUM_CLASS_IMAGES, CLASS_IMAGES_DIR, device)
    del temp_pipe
    torch.cuda.empty_cache() if device.type == "cuda" else None

    # Step 3: Setup LoRA
    print("\n" + "=" * 50)
    print("Step 3: Configuring LoRA Adapters")
    print("=" * 50)

    # Configure LoRA for U-Net attention layers
    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],  # Attention projections
        init_lora_weights="gaussian"
    )

    unet = get_peft_model(unet, lora_config)

    # Freeze everything except LoRA parameters
    vae.requires_grad_(False)
    text_encoder.requires_grad_(False)

    # Count trainable parameters
    trainable_params = sum(p.numel() for p in unet.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in unet.parameters())
    print(f"LoRA rank: {LORA_RANK}")
    print(f"Trainable parameters: {trainable_params:,} ({100*trainable_params/total_params:.2f}%)")
    print(f"Total U-Net parameters: {total_params:,}")

    # Step 4: Check for training data
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

    # Create dataset
    dataset = DreamBoothDataset(
        instance_data_root=TRAINING_IMAGES_DIR,
        class_data_root=CLASS_IMAGES_DIR,
        tokenizer=tokenizer,
        instance_prompt=INSTANCE_PROMPT,
        class_prompt=CLASS_PROMPT,
        size=512
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

    optimizer = torch.optim.AdamW(
        unet.parameters(),
        lr=LEARNING_RATE,
        betas=(0.9, 0.999),
        weight_decay=1e-2,
        eps=1e-8
    )

    lr_scheduler = get_scheduler(
        "constant",
        optimizer=optimizer,
        num_warmup_steps=0,
        num_training_steps=MAX_TRAIN_STEPS
    )

    print(f"Learning rate: {LEARNING_RATE}")
    print(f"Max training steps: {MAX_TRAIN_STEPS}")
    print(f"Prior preservation weight: {PRIOR_LOSS_WEIGHT}")

    # Prepare for training
    unet, optimizer, dataloader, lr_scheduler = accelerator.prepare(
        unet, optimizer, dataloader, lr_scheduler
    )

    vae.to(device)
    text_encoder.to(device)

    # Step 6: Training loop
    print("\n" + "=" * 50)
    print("Step 6: Training")
    print("=" * 50)

    global_step = 0
    losses = {"total": [], "instance": [], "prior": []}

    progress_bar = tqdm(total=MAX_TRAIN_STEPS, desc="Training")

    while global_step < MAX_TRAIN_STEPS:
        for batch in dataloader:
            with accelerator.accumulate(unet):
                # Process instance images (your subject)
                instance_latents = vae.encode(
                    batch["instance_images"].to(device)
                ).latent_dist.sample() * vae.config.scaling_factor

                # Process class images (for prior preservation)
                class_latents = vae.encode(
                    batch["class_images"].to(device)
                ).latent_dist.sample() * vae.config.scaling_factor

                # Sample noise
                instance_noise = torch.randn_like(instance_latents)
                class_noise = torch.randn_like(class_latents)

                # Sample timesteps
                bsz = instance_latents.shape[0]
                timesteps = torch.randint(
                    0, noise_scheduler.config.num_train_timesteps,
                    (bsz,), device=device
                ).long()

                # Add noise (forward diffusion - same as DDPM!)
                noisy_instance = noise_scheduler.add_noise(instance_latents, instance_noise, timesteps)
                noisy_class = noise_scheduler.add_noise(class_latents, class_noise, timesteps)

                # Get text embeddings
                instance_encoder_hidden = text_encoder(batch["instance_prompt_ids"].to(device))[0]
                class_encoder_hidden = text_encoder(batch["class_prompt_ids"].to(device))[0]

                # Predict noise for instance images
                instance_noise_pred = unet(noisy_instance, timesteps, instance_encoder_hidden).sample
                instance_loss = F.mse_loss(instance_noise_pred.float(), instance_noise.float())

                # Predict noise for class images (prior preservation)
                class_noise_pred = unet(noisy_class, timesteps, class_encoder_hidden).sample
                prior_loss = F.mse_loss(class_noise_pred.float(), class_noise.float())

                # Combined loss with prior preservation weight
                # This is the key DreamBooth innovation!
                loss = instance_loss + PRIOR_LOSS_WEIGHT * prior_loss

                accelerator.backward(loss)
                optimizer.step()
                lr_scheduler.step()
                optimizer.zero_grad()

            # Logging
            losses["total"].append(loss.item())
            losses["instance"].append(instance_loss.item())
            losses["prior"].append(prior_loss.item())

            if global_step % LOG_INTERVAL == 0:
                avg_loss = np.mean(losses["total"][-LOG_INTERVAL:])
                progress_bar.set_postfix({"loss": f"{avg_loss:.4f}"})

            # Save samples
            if global_step > 0 and global_step % SAMPLE_INTERVAL == 0:
                print(f"\n  Generating samples at step {global_step}...")
                save_progress_samples(
                    accelerator.unwrap_model(unet),
                    text_encoder, vae, tokenizer,
                    global_step, device, PROGRESS_DIR
                )

            # Save checkpoint
            if global_step > 0 and global_step % SAVE_INTERVAL == 0:
                print(f"\n  Saving checkpoint at step {global_step}...")
                checkpoint_dir = OUTPUT_DIR / f"checkpoint-{global_step}"
                accelerator.unwrap_model(unet).save_pretrained(checkpoint_dir)

            global_step += 1
            progress_bar.update(1)

            if global_step >= MAX_TRAIN_STEPS:
                break

    progress_bar.close()

    # Step 7: Save final model
    print("\n" + "=" * 50)
    print("Step 7: Saving Final LoRA Weights")
    print("=" * 50)

    # Save LoRA weights
    accelerator.unwrap_model(unet).save_pretrained(OUTPUT_DIR)
    print(f"Saved LoRA weights to: {OUTPUT_DIR}")

    # Calculate file size
    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("**/*") if f.is_file())
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")

    # Save loss curves
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.plot(losses["total"])
    plt.title("Total Loss")
    plt.xlabel("Step")
    plt.ylabel("Loss")
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 2)
    plt.plot(losses["instance"])
    plt.title("Instance Loss (Your Subject)")
    plt.xlabel("Step")
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 3, 3)
    plt.plot(losses["prior"])
    plt.title("Prior Preservation Loss")
    plt.xlabel("Step")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "exercise3b_loss_curves.png", dpi=150)
    plt.close()
    print(f"Saved loss curves to: {OUTPUTS_DIR / 'exercise3b_loss_curves.png'}")

    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"""
Output files:
- LoRA weights: {OUTPUT_DIR}/
- Progress samples: {PROGRESS_DIR}/
- Loss curves: {OUTPUTS_DIR / 'exercise3b_loss_curves.png'}

To use your trained LoRA:
    from diffusers import StableDiffusionPipeline

    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    pipe.load_lora_weights("{OUTPUT_DIR}")

    image = pipe("{INSTANCE_PROMPT}").images[0]

Key observations to reflect on:
1. How does the instance loss decrease over training?
2. Does the prior loss stay stable? (It should, if prior preservation works)
3. Compare early vs late checkpoint samples - do they improve?
4. Try prompts that weren't in training - does generalization work?
    """)

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train DreamBooth with LoRA")
    parser.add_argument("--max_steps", type=int, default=MAX_TRAIN_STEPS,
                        help="Maximum training steps")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE,
                        help="Learning rate")
    parser.add_argument("--lora_rank", type=int, default=LORA_RANK,
                        help="LoRA rank (higher = more capacity)")
    args = parser.parse_args()

    # Update config from args
    MAX_TRAIN_STEPS = args.max_steps
    LEARNING_RATE = args.lr
    LORA_RANK = args.lora_rank

    train_dreambooth_lora()
