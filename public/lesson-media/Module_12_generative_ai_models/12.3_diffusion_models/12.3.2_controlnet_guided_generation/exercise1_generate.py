import torch
import numpy as np
from PIL import Image
from pathlib import Path

# Local utilities
from controlnet_utils import (
    load_image,
    extract_canny_edges,
    get_fabric_sample_paths,
    create_comparison_grid
)

# Script configuration
SCRIPT_DIR = Path(__file__).parent
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
IMAGE_SIZE = 512
NUM_SAMPLES = 4
RANDOM_SEED = 42

# ControlNet generation settings
PROMPT = "African textile pattern with geometric designs, traditional fabric, vibrant colors"
NEGATIVE_PROMPT = "blurry, low quality, distorted, watermark"
GUIDANCE_SCALE = 7.5
CONTROLNET_SCALE = 0.8
NUM_INFERENCE_STEPS = 30

def check_dependencies():
    """Check that required libraries are installed."""
    try:
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
        return True
    except ImportError:
        print("Required libraries not found.")
        print("Please install with:")
        print("  pip install diffusers transformers accelerate")
        print("  pip install opencv-python")
        return False

def load_controlnet_pipeline():
    """
    Load the pretrained ControlNet pipeline.

    Uses the Canny ControlNet model which is trained to follow
    edge structures in the conditioning image.
    """
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

    print("Loading ControlNet (Canny) model...")
    print("This may take a few minutes on first run as models are downloaded.")

    # Load Canny ControlNet
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny",
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32
    )

    # Load Stable Diffusion pipeline with ControlNet
    pipeline = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
        safety_checker=None  # Disable for educational use
    )

    pipeline = pipeline.to(DEVICE)

    # Enable memory optimizations if available
    if DEVICE == 'cuda':
        try:
            pipeline.enable_xformers_memory_efficient_attention()
            print("Enabled xformers memory optimization")
        except Exception:
            pass

    return pipeline

def generate_with_controlnet(pipeline, control_image, seed=None):
    """
    Generate an image guided by the control image.

    Parameters
    ----------
    pipeline : StableDiffusionControlNetPipeline
        The loaded pipeline.
    control_image : PIL.Image
        The Canny edge image for conditioning.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    PIL.Image
        The generated image.
    """
    # Set seed for reproducibility
    generator = torch.Generator(device=DEVICE)
    if seed is not None:
        generator.manual_seed(seed)

    # Generate image
    result = pipeline(
        prompt=PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        image=control_image,
        num_inference_steps=NUM_INFERENCE_STEPS,
        guidance_scale=GUIDANCE_SCALE,
        controlnet_conditioning_scale=CONTROLNET_SCALE,
        generator=generator
    )

    return result.images[0]

def main():
    """Main exercise execution."""
    print("=" * 60)
    print("Exercise 1: Generate with Pretrained ControlNet")
    print("=" * 60)
    print()

    # Check dependencies
    if not check_dependencies():
        return

    print(f"Device: {DEVICE}")
    print(f"Image size: {IMAGE_SIZE}x{IMAGE_SIZE}")
    print()

    # Get sample fabric images
    fabric_paths = get_fabric_sample_paths(NUM_SAMPLES)

    if not fabric_paths:
        print("Error: Could not find African fabric images.")
        print("Please ensure the dataset exists at:")
        print("  ../12.1_generative_adversarial_networks/12.1.2_dcgan_art/african_fabric_processed/")
        return

    print(f"Found {len(fabric_paths)} fabric samples")
    print()

    # Load pipeline
    pipeline = load_controlnet_pipeline()
    print()

    # Process each fabric image
    results = []

    for i, fabric_path in enumerate(fabric_paths):
        print(f"Processing fabric {i+1}/{len(fabric_paths)}: {fabric_path.name}")

        # Load original image
        original, original_array = load_image(fabric_path, size=IMAGE_SIZE)

        # Extract Canny edges
        canny_edges = extract_canny_edges(original_array, low_threshold=100, high_threshold=200)

        # Generate with ControlNet
        seed = RANDOM_SEED + i
        generated = generate_with_controlnet(pipeline, canny_edges, seed=seed)

        # Store results
        results.append({
            'original': original,
            'canny': canny_edges,
            'generated': generated
        })

        print(f"  Generated image from seed {seed}")

    print()

    # Create output visualizations
    print("Creating output visualizations...")

    # Save individual comparison grids
    for i, result in enumerate(results):
        grid = create_comparison_grid(
            [result['original'], result['canny'], result['generated']],
            labels=['Original Fabric', 'Canny Edges', 'ControlNet Output'],
            title=f'Fabric {i+1}: Guided Generation'
        )
        grid.save(SCRIPT_DIR / f'exercise1_sample_{i+1}.png')

    # Create main output grid showing all results
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(results), 3, figsize=(12, 4 * len(results)), dpi=150)

    if len(results) == 1:
        axes = [axes]

    for i, result in enumerate(results):
        # Original
        axes[i][0].imshow(result['original'])
        axes[i][0].set_title('Original Fabric', fontsize=10)
        axes[i][0].axis('off')

        # Canny edges
        axes[i][1].imshow(result['canny'])
        axes[i][1].set_title('Canny Edges (Control)', fontsize=10)
        axes[i][1].axis('off')

        # Generated
        axes[i][2].imshow(result['generated'])
        axes[i][2].set_title('ControlNet Output', fontsize=10)
        axes[i][2].axis('off')

    plt.suptitle(
        'ControlNet Guided Generation from African Fabric Edges\n'
        f'Prompt: "{PROMPT[:60]}..."',
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise1_output.png', bbox_inches='tight', dpi=150)
    plt.close()

    print()
    print("=" * 60)
    print("Output saved to:")
    print(f"  - exercise1_output.png (main comparison grid)")
    for i in range(len(results)):
        print(f"  - exercise1_sample_{i+1}.png (individual comparison)")
    print()
    print("Reflection Questions:")
    print("-" * 40)
    print("1. How does the generated pattern relate to the original fabric?")
    print("   Look at how edges guide the structure while colors/textures differ.")
    print()
    print("2. What aspects of the original are preserved vs. changed?")
    print("   Consider: structure, symmetry, color palette, fine details.")
    print()
    print("3. How might different edge detection parameters affect results?")
    print("   The Canny thresholds (100, 200) determine edge sensitivity.")
    print()
    print("4. Compare this to DDPM output from Module 12.3.1.")
    print("   DDPM generates freely; ControlNet follows structure. Which is better?")
    print("=" * 60)

if __name__ == '__main__':
    main()
