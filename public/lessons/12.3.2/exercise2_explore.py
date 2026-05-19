import torch
import numpy as np
from PIL import Image
from pathlib import Path
import argparse

# Local utilities
from controlnet_utils import (
    load_image,
    extract_canny_edges,
    extract_lineart,
    get_fabric_sample_paths,
    create_comparison_grid,
    create_strength_sweep_grid
)

# Script configuration
SCRIPT_DIR = Path(__file__).parent
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
IMAGE_SIZE = 512
RANDOM_SEED = 42

# Default prompts
DEFAULT_PROMPT = "African textile pattern with geometric designs, traditional fabric, vibrant colors"
NEGATIVE_PROMPT = "blurry, low quality, distorted, watermark"

def load_canny_pipeline():
    """Load Canny ControlNet pipeline."""
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

    print("Loading Canny ControlNet...")
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny",
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32
    )

    pipeline = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
        safety_checker=None
    ).to(DEVICE)

    if DEVICE == 'cuda':
        try:
            pipeline.enable_xformers_memory_efficient_attention()
        except Exception:
            pass

    return pipeline

def load_lineart_pipeline():
    """Load Line Art ControlNet pipeline."""
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

    print("Loading Line Art ControlNet...")
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/control_v11p_sd15_lineart",
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32
    )

    pipeline = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
        safety_checker=None
    ).to(DEVICE)

    if DEVICE == 'cuda':
        try:
            pipeline.enable_xformers_memory_efficient_attention()
        except Exception:
            pass

    return pipeline

def generate_image(pipeline, control_image, prompt, controlnet_scale=0.8, seed=None):
    """Generate a single image with the given parameters."""
    generator = torch.Generator(device=DEVICE)
    if seed is not None:
        generator.manual_seed(seed)

    result = pipeline(
        prompt=prompt,
        negative_prompt=NEGATIVE_PROMPT,
        image=control_image,
        num_inference_steps=25,
        guidance_scale=7.5,
        controlnet_conditioning_scale=controlnet_scale,
        generator=generator
    )

    return result.images[0]

def part_a_control_comparison():
    """
    Part A: Compare Canny edges vs Line Art control types.

    Canny edges produce sharp, well-defined boundaries.
    Line art produces smoother, more artistic outlines.
    """
    print()
    print("=" * 60)
    print("Part A: Control Type Comparison")
    print("=" * 60)
    print()

    # Get a fabric sample
    fabric_paths = get_fabric_sample_paths(1)
    if not fabric_paths:
        print("Error: No fabric samples found")
        return

    # Load and process image
    original, original_array = load_image(fabric_paths[0], size=IMAGE_SIZE)

    # Extract different control types
    print("Extracting control signals...")
    canny_control = extract_canny_edges(original_array, low_threshold=100, high_threshold=200)
    lineart_control = extract_lineart(original_array, sigma=1.0)

    # Load pipelines
    canny_pipeline = load_canny_pipeline()

    # Generate with Canny
    print("Generating with Canny control...")
    canny_output = generate_image(
        canny_pipeline,
        canny_control,
        DEFAULT_PROMPT,
        controlnet_scale=0.8,
        seed=RANDOM_SEED
    )

    # Load lineart pipeline (releases canny from memory)
    del canny_pipeline
    torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    lineart_pipeline = load_lineart_pipeline()

    # Generate with Line Art
    print("Generating with Line Art control...")
    lineart_output = generate_image(
        lineart_pipeline,
        lineart_control,
        DEFAULT_PROMPT,
        controlnet_scale=0.8,
        seed=RANDOM_SEED
    )

    del lineart_pipeline
    torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    # Create comparison grid
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(15, 10), dpi=150)

    # Top row: Canny
    axes[0, 0].imshow(original)
    axes[0, 0].set_title('Original Fabric', fontsize=11)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(canny_control)
    axes[0, 1].set_title('Canny Edges', fontsize=11)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(canny_output)
    axes[0, 2].set_title('Canny ControlNet Output', fontsize=11)
    axes[0, 2].axis('off')

    # Bottom row: Line Art
    axes[1, 0].imshow(original)
    axes[1, 0].set_title('Original Fabric', fontsize=11)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(lineart_control)
    axes[1, 1].set_title('Line Art', fontsize=11)
    axes[1, 1].axis('off')

    axes[1, 2].imshow(lineart_output)
    axes[1, 2].set_title('Line Art ControlNet Output', fontsize=11)
    axes[1, 2].axis('off')

    plt.suptitle(
        'Control Type Comparison: Canny vs Line Art\n'
        'Notice how different edge extraction methods affect the final result',
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_control_comparison.png', bbox_inches='tight', dpi=150)
    plt.close()

    print()
    print("Saved: exercise2_control_comparison.png")
    print()
    print("Observations:")
    print("-" * 40)
    print("- Canny edges: Sharp, well-defined boundaries")
    print("- Line art: Smoother, more continuous lines")
    print("- Try adjusting Canny thresholds (100, 200) for different edge density")

def part_b_strength_sweep():
    """
    Part B: Explore different guidance strength values.

    controlnet_conditioning_scale controls how strictly the model
    follows the control image:
    - 0.0: Ignores control (like regular Stable Diffusion)
    - 0.5: Balanced between control and creativity
    - 1.0: Strict adherence to control structure
    """
    print()
    print("=" * 60)
    print("Part B: Guidance Strength Sweep")
    print("=" * 60)
    print()

    # Get a fabric sample
    fabric_paths = get_fabric_sample_paths(1)
    if not fabric_paths:
        print("Error: No fabric samples found")
        return

    # Load and extract edges
    original, original_array = load_image(fabric_paths[0], size=IMAGE_SIZE)
    canny_control = extract_canny_edges(original_array)

    # Load pipeline
    pipeline = load_canny_pipeline()

    # Guidance scales to test
    scales = [0.0, 0.3, 0.5, 0.7, 1.0]
    outputs = []

    print(f"Generating images at {len(scales)} guidance scales...")

    for scale in scales:
        print(f"  Scale {scale}...")
        output = generate_image(
            pipeline,
            canny_control,
            DEFAULT_PROMPT,
            controlnet_scale=scale,
            seed=RANDOM_SEED
        )
        outputs.append(output)

    del pipeline
    torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    # Create visualization
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(15, 10), dpi=150)
    axes = axes.flatten()

    # First cell: Original + Control
    combined = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE))
    # Create side-by-side mini version
    mini_orig = original.resize((IMAGE_SIZE // 2, IMAGE_SIZE // 2))
    mini_ctrl = canny_control.resize((IMAGE_SIZE // 2, IMAGE_SIZE // 2))
    axes[0].imshow(original)
    axes[0].set_title('Original + Canny Control', fontsize=10)
    axes[0].axis('off')

    # Generated images
    for i, (scale, output) in enumerate(zip(scales, outputs)):
        axes[i + 1].imshow(output)
        axes[i + 1].set_title(f'Scale = {scale}', fontsize=11, fontweight='bold')
        axes[i + 1].axis('off')

    plt.suptitle(
        'ControlNet Guidance Strength Sweep\n'
        '0.0 = Ignore control (free generation) | 1.0 = Strict adherence',
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_strength_sweep.png', bbox_inches='tight', dpi=150)
    plt.close()

    print()
    print("Saved: exercise2_strength_sweep.png")
    print()
    print("Observations:")
    print("-" * 40)
    print("- Scale 0.0: Control is ignored, generation is free (like vanilla SD)")
    print("- Scale 0.3-0.5: Soft guidance, structure suggested but not enforced")
    print("- Scale 0.7-0.8: Good balance (recommended for most uses)")
    print("- Scale 1.0: Strict adherence, may lose creative freedom")

def part_c_prompt_variation():
    """
    Part C: Same control image, different prompts.

    This demonstrates how text prompts interact with spatial control.
    The structure comes from ControlNet, but style/colors from the prompt.
    """
    print()
    print("=" * 60)
    print("Part C: Prompt Variation")
    print("=" * 60)
    print()

    # Get a fabric sample
    fabric_paths = get_fabric_sample_paths(1)
    if not fabric_paths:
        print("Error: No fabric samples found")
        return

    # Load and extract edges
    original, original_array = load_image(fabric_paths[0], size=IMAGE_SIZE)
    canny_control = extract_canny_edges(original_array)

    # Different prompts
    prompts = [
        "African textile pattern, traditional fabric, vibrant red and gold",
        "Japanese kimono pattern, silk fabric, blue and white",
        "Abstract digital art, neon colors, cyberpunk style",
        "Watercolor painting, soft pastels, artistic texture"
    ]

    # Load pipeline
    pipeline = load_canny_pipeline()

    outputs = []
    print(f"Generating {len(prompts)} variations...")

    for i, prompt in enumerate(prompts):
        print(f"  Prompt {i+1}: {prompt[:40]}...")
        output = generate_image(
            pipeline,
            canny_control,
            prompt,
            controlnet_scale=0.7,
            seed=RANDOM_SEED
        )
        outputs.append((prompt, output))

    del pipeline
    torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    # Create visualization
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 3, figsize=(15, 10), dpi=150)
    axes = axes.flatten()

    # Control image
    axes[0].imshow(canny_control)
    axes[0].set_title('Canny Control (same for all)', fontsize=10)
    axes[0].axis('off')

    # Hide one cell
    axes[5].axis('off')

    # Generated images
    for i, (prompt, output) in enumerate(outputs):
        axes[i + 1].imshow(output)
        # Truncate prompt for title
        short_prompt = prompt[:35] + '...' if len(prompt) > 35 else prompt
        axes[i + 1].set_title(short_prompt, fontsize=9)
        axes[i + 1].axis('off')

    plt.suptitle(
        'Prompt Variation: Same Structure, Different Styles\n'
        'ControlNet provides structure; prompt provides style and color',
        fontsize=12, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_prompt_variation.png', bbox_inches='tight', dpi=150)
    plt.close()

    print()
    print("Saved: exercise2_prompt_variation.png")
    print()
    print("Observations:")
    print("-" * 40)
    print("- Same edge structure appears in all outputs")
    print("- Colors, textures, and styles differ based on prompt")
    print("- ControlNet separates structure control from style control")
    print("- This is a key advantage over pure text-to-image generation")

def main():
    """Run all exploration parts or a specific one."""
    parser = argparse.ArgumentParser(description='Exercise 2: Explore ControlNet Parameters')
    parser.add_argument('--part', choices=['a', 'b', 'c', 'all'], default='all',
                        help='Which part to run (a=control types, b=strength, c=prompts, all=everything)')

    args = parser.parse_args()

    print("=" * 60)
    print("Exercise 2: Explore Control Types and Parameters")
    print("=" * 60)
    print()
    print(f"Device: {DEVICE}")
    print(f"Running: Part {args.part.upper()}")

    # Check dependencies
    try:
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
    except ImportError:
        print("\nRequired libraries not found.")
        print("Please install with:")
        print("  pip install diffusers transformers accelerate")
        return

    if args.part in ['a', 'all']:
        part_a_control_comparison()

    if args.part in ['b', 'all']:
        part_b_strength_sweep()

    if args.part in ['c', 'all']:
        part_c_prompt_variation()

    print()
    print("=" * 60)
    print("Exercise 2 Complete!")
    print()
    print("Suggested Modifications:")
    print("-" * 40)
    print("1. Change Canny thresholds in controlnet_utils.py")
    print("2. Try different fabric samples from the dataset")
    print("3. Experiment with more extreme guidance scales (1.5+)")
    print("4. Combine your own prompts with African fabric structure")
    print("=" * 60)

if __name__ == '__main__':
    main()
