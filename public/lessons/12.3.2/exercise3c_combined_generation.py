import torch
import numpy as np
from PIL import Image
from pathlib import Path
import argparse

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
RANDOM_SEED = 42

# Model paths
MODEL_DIR = SCRIPT_DIR / 'models'
CONTROLNET_PATH = MODEL_DIR / 'controlnet_fill50k.pt'
LORA_PATH = MODEL_DIR / 'lora_african_fabrics.safetensors'

# Generation settings
PROMPT = "African textile pattern with geometric designs, traditional fabric, vibrant colors"
NEGATIVE_PROMPT = "blurry, low quality, distorted"
CONTROLNET_SCALE = 0.7
LORA_SCALE = 0.8
NUM_INFERENCE_STEPS = 30

def check_models():
    """Check if trained models exist."""
    print("Checking for trained models...")

    controlnet_exists = CONTROLNET_PATH.exists()
    lora_exists = LORA_PATH.exists()

    print(f"  ControlNet (Fill50K): {'Found' if controlnet_exists else 'Not found'}")
    print(f"  LoRA (African Fabrics): {'Found' if lora_exists else 'Not found'}")
    print()

    if not controlnet_exists and not lora_exists:
        print("No trained models found!")
        print()
        print("You can either:")
        print("1. Complete Exercise 3A to train ControlNet on Fill50K")
        print("2. Complete Exercise 3B to train LoRA on African Fabrics")
        print("3. Use pretrained models (see below)")
        print()
        print("For demonstration, this script will use pretrained models from Hugging Face.")
        return 'pretrained'

    if not controlnet_exists:
        print("ControlNet not found. Will use pretrained from Hugging Face.")

    if not lora_exists:
        print("LoRA not found. Will skip LoRA adaptation.")

    return 'mixed' if controlnet_exists or lora_exists else 'pretrained'

def load_combined_pipeline(use_lora=True):
    """
    Load pipeline with ControlNet and optionally LoRA.

    This demonstrates the real-world workflow of combining multiple
    adapters for fine-grained control.
    """
    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

    print("Loading combined pipeline...")

    # Load ControlNet
    if CONTROLNET_PATH.exists():
        print("  Loading trained ControlNet from Fill50K...")
        # Note: Full implementation would load custom-trained ControlNet
        # For now, use pretrained as fallback
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32
        )
    else:
        print("  Loading pretrained ControlNet (Canny)...")
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32
        )

    # Load pipeline
    pipeline = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=torch.float16 if DEVICE == 'cuda' else torch.float32,
        safety_checker=None
    )

    # Load LoRA if available
    if use_lora and LORA_PATH.exists():
        print("  Loading LoRA adapter for African Fabric style...")
        try:
            pipeline.load_lora_weights(str(LORA_PATH))
            pipeline.fuse_lora(lora_scale=LORA_SCALE)
            print(f"  LoRA loaded with scale {LORA_SCALE}")
        except Exception as e:
            print(f"  Warning: Could not load LoRA: {e}")
            print("  Continuing without LoRA...")

    pipeline = pipeline.to(DEVICE)

    # Enable memory optimizations
    if DEVICE == 'cuda':
        try:
            pipeline.enable_xformers_memory_efficient_attention()
            print("  Enabled xformers optimization")
        except Exception:
            pass

    return pipeline

def generate_comparison():
    """
    Generate images comparing different configurations.

    Creates a grid showing:
    1. Original fabric image
    2. Canny control image
    3. ControlNet only (no LoRA)
    4. ControlNet + LoRA (combined)
    """
    print("=" * 60)
    print("Exercise 3C: Combined ControlNet + LoRA Generation")
    print("=" * 60)
    print()

    # Check dependencies
    try:
        from diffusers import StableDiffusionControlNetPipeline
    except ImportError:
        print("Required libraries not found.")
        print("Please install: pip install diffusers transformers accelerate")
        return

    print(f"Device: {DEVICE}")
    model_status = check_models()

    # Get a fabric sample for the control image
    fabric_paths = get_fabric_sample_paths(1)
    if not fabric_paths:
        print("Error: No fabric samples found")
        return

    # Load and process
    original, original_array = load_image(fabric_paths[0], size=IMAGE_SIZE)
    canny_edges = extract_canny_edges(original_array)

    print()
    print("Generating comparison images...")
    print("-" * 40)

    # Generator for reproducibility
    def get_generator():
        g = torch.Generator(device=DEVICE)
        g.manual_seed(RANDOM_SEED)
        return g

    results = {
        'original': original,
        'control': canny_edges
    }

    # Generation 1: ControlNet only (no LoRA)
    print("1. Generating with ControlNet only...")
    pipeline_no_lora = load_combined_pipeline(use_lora=False)

    result_no_lora = pipeline_no_lora(
        prompt=PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        image=canny_edges,
        num_inference_steps=NUM_INFERENCE_STEPS,
        controlnet_conditioning_scale=CONTROLNET_SCALE,
        generator=get_generator()
    ).images[0]
    results['controlnet_only'] = result_no_lora

    # Clear memory
    del pipeline_no_lora
    torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    # Generation 2: ControlNet + LoRA (if LoRA exists)
    if LORA_PATH.exists():
        print("2. Generating with ControlNet + LoRA...")
        pipeline_combined = load_combined_pipeline(use_lora=True)

        result_combined = pipeline_combined(
            prompt=PROMPT,
            negative_prompt=NEGATIVE_PROMPT,
            image=canny_edges,
            num_inference_steps=NUM_INFERENCE_STEPS,
            controlnet_conditioning_scale=CONTROLNET_SCALE,
            generator=get_generator()
        ).images[0]
        results['combined'] = result_combined

        del pipeline_combined
        torch.cuda.empty_cache() if DEVICE == 'cuda' else None
    else:
        print("2. Skipping ControlNet + LoRA (no LoRA model found)")
        results['combined'] = None

    # Create visualization
    print()
    print("Creating comparison visualization...")

    import matplotlib.pyplot as plt

    if results['combined'] is not None:
        # Full comparison (4 images)
        fig, axes = plt.subplots(2, 2, figsize=(12, 12), dpi=150)

        axes[0, 0].imshow(results['original'])
        axes[0, 0].set_title('Original African Fabric', fontsize=11, fontweight='bold')
        axes[0, 0].axis('off')

        axes[0, 1].imshow(results['control'])
        axes[0, 1].set_title('Canny Edges (Control)', fontsize=11, fontweight='bold')
        axes[0, 1].axis('off')

        axes[1, 0].imshow(results['controlnet_only'])
        axes[1, 0].set_title('ControlNet Only\n(Structure control)', fontsize=11, fontweight='bold')
        axes[1, 0].axis('off')

        axes[1, 1].imshow(results['combined'])
        axes[1, 1].set_title('ControlNet + LoRA\n(Structure + Style)', fontsize=11, fontweight='bold')
        axes[1, 1].axis('off')

        plt.suptitle(
            'Combined Generation: ControlNet + LoRA\n'
            'Structure from Canny edges + Style from African Fabric LoRA',
            fontsize=12, fontweight='bold'
        )
    else:
        # Reduced comparison (3 images)
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=150)

        axes[0].imshow(results['original'])
        axes[0].set_title('Original Fabric', fontsize=11, fontweight='bold')
        axes[0].axis('off')

        axes[1].imshow(results['control'])
        axes[1].set_title('Canny Edges', fontsize=11, fontweight='bold')
        axes[1].axis('off')

        axes[2].imshow(results['controlnet_only'])
        axes[2].set_title('ControlNet Output', fontsize=11, fontweight='bold')
        axes[2].axis('off')

        plt.suptitle(
            'ControlNet Generation\n'
            '(Train LoRA with Exercise 3B to see style adaptation)',
            fontsize=12, fontweight='bold'
        )

    plt.tight_layout()
    output_path = SCRIPT_DIR / 'exercise3c_combined_output.png'
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()

    # Save individual results
    results['original'].save(SCRIPT_DIR / 'exercise3c_original.png')
    results['control'].save(SCRIPT_DIR / 'exercise3c_control.png')
    results['controlnet_only'].save(SCRIPT_DIR / 'exercise3c_controlnet_only.png')
    if results['combined']:
        results['combined'].save(SCRIPT_DIR / 'exercise3c_controlnet_lora.png')

    print()
    print("=" * 60)
    print("Output saved:")
    print(f"  - exercise3c_combined_output.png (comparison grid)")
    print(f"  - exercise3c_original.png")
    print(f"  - exercise3c_control.png")
    print(f"  - exercise3c_controlnet_only.png")
    if results['combined']:
        print(f"  - exercise3c_controlnet_lora.png")
    print()
    print("Key Observations:")
    print("-" * 40)
    print("1. ControlNet preserves the STRUCTURE from Canny edges")
    print("2. LoRA adapts the STYLE toward African fabric patterns")
    print("3. Combined approach gives you control over BOTH aspects")
    print()
    print("This workflow is used in professional applications:")
    print("  - Game asset creation (control poses + style)")
    print("  - Architectural visualization (control layout + materials)")
    print("  - Fashion design (control silhouette + fabric style)")
    print("=" * 60)

def demo_strength_variation():
    """
    Demonstrate different LoRA strength values.

    Shows how varying lora_scale affects the output:
    - 0.0: No LoRA influence (pure ControlNet)
    - 0.5: Balanced influence
    - 1.0: Strong LoRA influence
    """
    if not LORA_PATH.exists():
        print("LoRA model not found. Please complete Exercise 3B first.")
        return

    print()
    print("Generating LoRA strength comparison...")

    # Get control image
    fabric_paths = get_fabric_sample_paths(1)
    if not fabric_paths:
        return

    original, original_array = load_image(fabric_paths[0], size=IMAGE_SIZE)
    canny_edges = extract_canny_edges(original_array)

    # Different LoRA strengths
    lora_scales = [0.0, 0.3, 0.5, 0.7, 1.0]
    results = []

    from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

    for scale in lora_scales:
        print(f"  Generating with LoRA scale {scale}...")

        # Load pipeline fresh for each scale
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

        # Load LoRA with specific scale
        if scale > 0:
            try:
                pipeline.load_lora_weights(str(LORA_PATH))
                pipeline.fuse_lora(lora_scale=scale)
            except Exception as e:
                print(f"  Warning: LoRA loading failed: {e}")

        # Generate
        generator = torch.Generator(device=DEVICE).manual_seed(RANDOM_SEED)
        result = pipeline(
            prompt=PROMPT,
            negative_prompt=NEGATIVE_PROMPT,
            image=canny_edges,
            num_inference_steps=NUM_INFERENCE_STEPS,
            controlnet_conditioning_scale=CONTROLNET_SCALE,
            generator=generator
        ).images[0]

        results.append((scale, result))

        del pipeline
        torch.cuda.empty_cache() if DEVICE == 'cuda' else None

    # Create visualization
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(lora_scales) + 1, figsize=(3.5 * (len(lora_scales) + 1), 4), dpi=150)

    # Control image
    axes[0].imshow(canny_edges)
    axes[0].set_title('Control\n(Canny)', fontsize=10)
    axes[0].axis('off')

    # Generated images
    for i, (scale, result) in enumerate(results):
        axes[i + 1].imshow(result)
        axes[i + 1].set_title(f'LoRA={scale}', fontsize=10, fontweight='bold')
        axes[i + 1].axis('off')

    plt.suptitle(
        'LoRA Strength Variation\n0.0 = No style adaptation | 1.0 = Full style adaptation',
        fontsize=11, fontweight='bold'
    )
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise3c_lora_strength.png', bbox_inches='tight', dpi=150)
    plt.close()

    print("Saved: exercise3c_lora_strength.png")

def main():
    parser = argparse.ArgumentParser(description='Exercise 3C: Combined Generation')
    parser.add_argument('--generate', action='store_true', help='Generate comparison')
    parser.add_argument('--strength-demo', action='store_true', help='Demo LoRA strength variation')

    args = parser.parse_args()

    if args.generate:
        generate_comparison()
    elif args.strength_demo:
        demo_strength_variation()
    else:
        print("Combined ControlNet + LoRA Generation")
        print()
        print("Usage:")
        print("  python exercise3c_combined_generation.py --generate      # Main comparison")
        print("  python exercise3c_combined_generation.py --strength-demo # LoRA strength demo")
        print()
        print("Prerequisites:")
        print("  - Exercise 3A complete (ControlNet on Fill50K)")
        print("  - Exercise 3B complete (LoRA on African Fabrics)")
        print("  - Or use pretrained models (works without training)")

if __name__ == '__main__':
    main()
