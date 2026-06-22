import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Check for required libraries
try:
    import torch
except ImportError:
    print("Error: PyTorch not found. Please install with: pip install torch")
    sys.exit(1)

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
except ImportError:
    print("Error: diffusers library not found.")
    print("Please install with: pip install diffusers transformers accelerate")
    sys.exit(1)

# =============================================================================
# Configuration
# =============================================================================

# Default model configuration
DEFAULT_MODEL_ID = "runwayml/stable-diffusion-v1-5"
DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Paths relative to this file
MODULE_DIR = Path(__file__).parent
MODELS_DIR = MODULE_DIR / "models"
OUTPUTS_DIR = MODULE_DIR / "outputs"
TRAINING_IMAGES_DIR = MODULE_DIR / "training_images"

# =============================================================================
# Model Loading Functions
# =============================================================================

def load_base_pipeline(model_id=DEFAULT_MODEL_ID, device=DEFAULT_DEVICE,
                       use_fp16=True, use_fast_scheduler=True):
    """
    Load the base Stable Diffusion pipeline.

    Parameters:
        model_id: Hugging Face model identifier or local path
        device: Device to load model on ('cuda' or 'cpu')
        use_fp16: Use half-precision for memory efficiency
        use_fast_scheduler: Use DPMSolver for faster inference

    Returns:
        StableDiffusionPipeline: Loaded pipeline ready for inference
    """
    print(f"Loading base model: {model_id}")
    print(f"Device: {device}")

    # Determine dtype based on device and user preference
    if device == "cuda" and use_fp16:
        dtype = torch.float16
    else:
        dtype = torch.float32

    # Load the pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        safety_checker=None,  # Disable for educational use
        requires_safety_checker=False
    )

    # Use faster scheduler if requested
    if use_fast_scheduler:
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            pipe.scheduler.config
        )

    pipe = pipe.to(device)

    # Enable memory optimizations if available
    if device == "cuda":
        try:
            pipe.enable_xformers_memory_efficient_attention()
            print("Enabled xformers memory efficient attention")
        except Exception:
            # xformers not available, continue without it
            pass

    print("Base model loaded successfully!")
    return pipe

def load_lora_weights(pipe, lora_path):
    """
    Load LoRA weights into an existing pipeline.

    Parameters:
        pipe: StableDiffusionPipeline instance
        lora_path: Path to LoRA weights directory or file

    Returns:
        StableDiffusionPipeline: Pipeline with LoRA weights loaded
    """
    lora_path = Path(lora_path)

    if not lora_path.exists():
        print(f"Warning: LoRA weights not found at '{lora_path}'")
        print("\nTo use pre-trained LoRA weights:")
        print("1. Complete Exercise 3 to train your own model, OR")
        print("2. Download pre-trained weights from the course repository")
        print("\nContinuing with base model (no personalization)...")
        return pipe

    print(f"Loading LoRA weights from: {lora_path}")
    pipe.load_lora_weights(str(lora_path))
    print("LoRA weights loaded successfully!")

    return pipe

def load_textual_inversion(pipe, embedding_path, token="<african-fabric>"):
    """
    Load Textual Inversion embedding into an existing pipeline.

    Parameters:
        pipe: StableDiffusionPipeline instance
        embedding_path: Path to learned embedding file (.safetensors or .bin)
        token: The placeholder token associated with the embedding

    Returns:
        StableDiffusionPipeline: Pipeline with embedding loaded
    """
    embedding_path = Path(embedding_path)

    if not embedding_path.exists():
        print(f"Warning: Textual Inversion embedding not found at '{embedding_path}'")
        print("\nTo use pre-trained embedding:")
        print("1. Complete Exercise 3a to train your own embedding, OR")
        print("2. Download pre-trained embedding from the course repository")
        print("\nContinuing with base model (no personalization)...")
        return pipe

    print(f"Loading Textual Inversion embedding from: {embedding_path}")
    pipe.load_textual_inversion(str(embedding_path), token=token)
    print(f"Embedding loaded for token: {token}")

    return pipe

# =============================================================================
# Image Processing Functions
# =============================================================================

def load_training_images(image_dir=TRAINING_IMAGES_DIR, size=(512, 512)):
    """
    Load and preprocess training images for DreamBooth.

    Parameters:
        image_dir: Directory containing training images
        size: Target size (width, height) for images

    Returns:
        list: List of PIL Image objects
    """
    image_dir = Path(image_dir)

    if not image_dir.exists():
        print(f"Error: Training images directory not found: {image_dir}")
        return []

    # Supported image formats
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']

    images = []
    for ext in extensions:
        images.extend(image_dir.glob(f"*{ext}"))
        images.extend(image_dir.glob(f"*{ext.upper()}"))

    if not images:
        print(f"Warning: No images found in {image_dir}")
        return []

    print(f"Found {len(images)} training images")

    # Load and preprocess
    processed_images = []
    for img_path in sorted(images):
        img = Image.open(img_path).convert("RGB")
        img = img.resize(size, Image.Resampling.LANCZOS)
        processed_images.append(img)

    return processed_images

def create_image_grid(images, rows=None, cols=None, padding=2,
                      background_color=(255, 255, 255)):
    """
    Arrange multiple images into a grid.

    Parameters:
        images: List of PIL Images or numpy arrays
        rows: Number of rows (auto-calculated if None)
        cols: Number of columns (auto-calculated if None)
        padding: Pixels between images
        background_color: RGB tuple for background

    Returns:
        PIL.Image: Combined grid image
    """
    n_images = len(images)

    if n_images == 0:
        raise ValueError("No images provided")

    # Convert to PIL if needed
    pil_images = []
    for img in images:
        if isinstance(img, np.ndarray):
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)
            pil_images.append(Image.fromarray(img))
        else:
            pil_images.append(img)

    # Auto-calculate grid dimensions
    if rows is None and cols is None:
        cols = int(np.ceil(np.sqrt(n_images)))
        rows = int(np.ceil(n_images / cols))
    elif rows is None:
        rows = int(np.ceil(n_images / cols))
    elif cols is None:
        cols = int(np.ceil(n_images / rows))

    # Get image dimensions (assume all same size)
    img_width, img_height = pil_images[0].size

    # Calculate grid dimensions
    grid_width = cols * img_width + (cols + 1) * padding
    grid_height = rows * img_height + (rows + 1) * padding

    # Create grid
    grid = Image.new("RGB", (grid_width, grid_height), background_color)

    # Place images
    for idx, img in enumerate(pil_images):
        if idx >= rows * cols:
            break
        row = idx // cols
        col = idx % cols
        x = padding + col * (img_width + padding)
        y = padding + row * (img_height + padding)
        grid.paste(img, (x, y))

    return grid

def save_comparison_grid(images, labels, output_path, title=None,
                         rows=None, cols=None, figsize=(12, 8)):
    """
    Create and save a labeled comparison grid using matplotlib.

    Parameters:
        images: List of PIL Images or numpy arrays
        labels: List of labels for each image
        output_path: Path to save the figure
        title: Optional title for the grid
        rows: Number of rows
        cols: Number of columns
        figsize: Figure size in inches
    """
    n_images = len(images)

    if cols is None:
        cols = min(4, n_images)
    if rows is None:
        rows = int(np.ceil(n_images / cols))

    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    axes = np.atleast_2d(axes)

    for idx in range(rows * cols):
        row = idx // cols
        col = idx % cols
        ax = axes[row, col]

        if idx < n_images:
            img = images[idx]
            if isinstance(img, Image.Image):
                img = np.array(img)
            ax.imshow(img)
            if idx < len(labels):
                ax.set_title(labels[idx], fontsize=10)

        ax.axis('off')

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved comparison grid to: {output_path}")

# =============================================================================
# Generation Functions
# =============================================================================

def generate_images(pipe, prompts, num_images_per_prompt=1,
                    num_inference_steps=30, guidance_scale=7.5,
                    seed=None, device=DEFAULT_DEVICE):
    """
    Generate images from text prompts.

    Parameters:
        pipe: StableDiffusionPipeline instance
        prompts: Single prompt string or list of prompts
        num_images_per_prompt: Number of images to generate per prompt
        num_inference_steps: Number of denoising steps
        guidance_scale: Classifier-free guidance scale
        seed: Random seed for reproducibility
        device: Device for generation

    Returns:
        list: List of generated PIL Images
    """
    if isinstance(prompts, str):
        prompts = [prompts]

    # Set random seed if provided
    generator = None
    if seed is not None:
        generator = torch.Generator(device=device).manual_seed(seed)

    all_images = []

    for prompt in prompts:
        print(f"Generating: '{prompt[:50]}...' " if len(prompt) > 50 else f"Generating: '{prompt}'")

        with torch.no_grad():
            result = pipe(
                prompt,
                num_images_per_prompt=num_images_per_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )

        all_images.extend(result.images)

    return all_images

# =============================================================================
# Training Visualization Functions
# =============================================================================

def create_training_progress_grid(checkpoint_images, step_numbers,
                                   training_images=None, output_path=None):
    """
    Create a visualization showing training progress over steps.

    Parameters:
        checkpoint_images: List of generated images at each checkpoint
        step_numbers: List of step numbers corresponding to images
        training_images: Optional list of training images for comparison
        output_path: Path to save the visualization

    Returns:
        PIL.Image: Progress visualization grid
    """
    n_checkpoints = len(checkpoint_images)

    # Calculate layout
    if training_images:
        rows = 2
        cols = max(n_checkpoints, len(training_images))
    else:
        rows = 1
        cols = n_checkpoints

    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    if rows == 1:
        axes = axes.reshape(1, -1)

    # Plot checkpoint images
    for idx, (img, step) in enumerate(zip(checkpoint_images, step_numbers)):
        ax = axes[0, idx] if rows > 1 else axes[0, idx]
        if isinstance(img, Image.Image):
            img = np.array(img)
        ax.imshow(img)
        ax.set_title(f"Step {step}", fontsize=10)
        ax.axis('off')

    # Plot training images if provided
    if training_images:
        for idx, img in enumerate(training_images):
            if idx >= cols:
                break
            ax = axes[1, idx]
            if isinstance(img, Image.Image):
                img = np.array(img)
            ax.imshow(img)
            if idx == 0:
                ax.set_title("Training Images", fontsize=10)
            ax.axis('off')

        # Clear unused axes
        for idx in range(len(training_images), cols):
            axes[1, idx].axis('off')

    # Clear unused axes in first row
    for idx in range(n_checkpoints, cols):
        axes[0, idx].axis('off')

    plt.suptitle("Training Progress: Generated Samples Over Training Steps",
                 fontsize=12, fontweight='bold')
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved training progress to: {output_path}")

    # Convert to PIL for return
    fig.canvas.draw()
    img_array = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img_array = img_array.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close()

    return Image.fromarray(img_array)

def plot_loss_curves(losses, output_path, title="Training Loss"):
    """
    Plot and save training loss curves.

    Parameters:
        losses: Dictionary with loss names as keys and lists of values
        output_path: Path to save the plot
        title: Plot title
    """
    plt.figure(figsize=(10, 6))

    for name, values in losses.items():
        steps = range(1, len(values) + 1)
        plt.plot(steps, values, label=name, linewidth=2)

    plt.xlabel("Training Step", fontsize=12)
    plt.ylabel("Loss", fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"Saved loss curves to: {output_path}")

# =============================================================================
# Utility Functions
# =============================================================================

def print_section_header(title, width=60):
    """Print a formatted section header."""
    print("=" * width)
    print(title.center(width))
    print("=" * width)

def check_gpu_memory():
    """Print GPU memory usage if CUDA is available."""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**3
        reserved = torch.cuda.memory_reserved() / 1024**3
        print(f"GPU Memory: {allocated:.2f} GB allocated, {reserved:.2f} GB reserved")
    else:
        print("GPU: Not available (using CPU)")

def get_device():
    """Get the best available device."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print_section_header("DreamBooth Utilities Test")

    print("\nChecking environment...")
    print(f"PyTorch version: {torch.__version__}")
    print(f"Device: {get_device()}")
    check_gpu_memory()

    print("\nModule directory:", MODULE_DIR)
    print("Models directory:", MODELS_DIR)
    print("Outputs directory:", OUTPUTS_DIR)
    print("Training images directory:", TRAINING_IMAGES_DIR)

    print("\nUtilities loaded successfully!")
    print("\nAvailable functions:")
    print("  - load_base_pipeline()")
    print("  - load_lora_weights()")
    print("  - load_textual_inversion()")
    print("  - load_training_images()")
    print("  - create_image_grid()")
    print("  - save_comparison_grid()")
    print("  - generate_images()")
    print("  - create_training_progress_grid()")
    print("  - plot_loss_curves()")
