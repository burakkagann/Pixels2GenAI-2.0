import os
import sys
from pathlib import Path

# Add module directory to path for imports
MODULE_DIR = Path(__file__).parent
sys.path.insert(0, str(MODULE_DIR))

import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# Import our utilities
from dreambooth_utils import (
    load_base_pipeline,
    load_lora_weights,
    generate_images,
    create_image_grid,
    save_comparison_grid,
    print_section_header,
    get_device,
    check_gpu_memory,
    MODELS_DIR,
    OUTPUTS_DIR
)

# =============================================================================
# Configuration - Modify these values to experiment!
# =============================================================================

# The special token that represents our African fabric concept
# This was learned during DreamBooth training
SUBJECT_TOKEN = "sks"
CLASS_NAME = "african fabric pattern"

# Path to pre-trained LoRA weights
LORA_PATH = MODELS_DIR / "fabric_lora"

# Generation settings
NUM_INFERENCE_STEPS = 30    # More steps = higher quality, slower
GUIDANCE_SCALE = 7.5        # Higher = more adherence to prompt
RANDOM_SEED = 42            # For reproducible results

# Prompts showcasing the personalized subject in different contexts
GENERATION_PROMPTS = [
    # Basic fabric pattern
    f"a {SUBJECT_TOKEN} {CLASS_NAME}, vibrant colors, detailed texture",

    # Fashion application
    f"a beautiful dress made of {SUBJECT_TOKEN} {CLASS_NAME}, fashion photography",

    # Interior design
    f"{SUBJECT_TOKEN} {CLASS_NAME} as wallpaper in a modern living room",

    # Artistic interpretation
    f"a watercolor painting of {SUBJECT_TOKEN} {CLASS_NAME}",

    # Product design
    f"a handbag featuring {SUBJECT_TOKEN} {CLASS_NAME}, product photography",

    # Mixed media
    f"{SUBJECT_TOKEN} {CLASS_NAME} texture on ceramic vase, studio lighting",

    # Digital art
    f"{SUBJECT_TOKEN} {CLASS_NAME} in cyberpunk style, neon lights",

    # Traditional context
    f"traditional {SUBJECT_TOKEN} {CLASS_NAME} on woven basket",

    # Abstract
    f"abstract geometric art inspired by {SUBJECT_TOKEN} {CLASS_NAME}",
]

# =============================================================================
# Main Generation Script
# =============================================================================

def main():
    """Main function to generate fabric patterns with DreamBooth model."""

    print_section_header("Exercise 1: Generate with Personalized DreamBooth Model")

    # Check device
    device = get_device()
    print(f"\nDevice: {device}")
    if device == "cuda":
        check_gpu_memory()

    # Create output directory
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Load the base Stable Diffusion pipeline
    print("\n" + "=" * 50)
    print("Step 1: Loading Base Model")
    print("=" * 50)

    pipe = load_base_pipeline(
        use_fp16=(device == "cuda"),
        use_fast_scheduler=True
    )

    # Step 2: Load the personalized LoRA weights
    print("\n" + "=" * 50)
    print("Step 2: Loading Personalized LoRA Weights")
    print("=" * 50)

    pipe = load_lora_weights(pipe, LORA_PATH)

    # Step 3: Generate images with various prompts
    print("\n" + "=" * 50)
    print("Step 3: Generating Personalized Fabric Patterns")
    print("=" * 50)

    print(f"\nGenerating {len(GENERATION_PROMPTS)} images...")
    print(f"  Inference steps: {NUM_INFERENCE_STEPS}")
    print(f"  Guidance scale: {GUIDANCE_SCALE}")
    print(f"  Random seed: {RANDOM_SEED}")

    all_images = []
    all_labels = []

    for i, prompt in enumerate(GENERATION_PROMPTS):
        print(f"\n[{i+1}/{len(GENERATION_PROMPTS)}] Generating...")

        # Generate image
        images = generate_images(
            pipe,
            prompt,
            num_images_per_prompt=1,
            num_inference_steps=NUM_INFERENCE_STEPS,
            guidance_scale=GUIDANCE_SCALE,
            seed=RANDOM_SEED + i,  # Different seed per image for variety
            device=device
        )

        all_images.extend(images)

        # Create short label for display
        label = prompt[:40] + "..." if len(prompt) > 40 else prompt
        all_labels.append(label)

    # Step 4: Create and save output grid
    print("\n" + "=" * 50)
    print("Step 4: Creating Output Visualization")
    print("=" * 50)

    # Save individual images
    individual_dir = OUTPUTS_DIR / "exercise1_variations"
    individual_dir.mkdir(exist_ok=True)

    for i, (img, prompt) in enumerate(zip(all_images, GENERATION_PROMPTS)):
        # Create safe filename from prompt
        safe_name = prompt[:30].replace(" ", "_").replace(",", "")
        img.save(individual_dir / f"{i+1:02d}_{safe_name}.png")

    print(f"Saved {len(all_images)} individual images to: {individual_dir}")

    # Create comparison grid with matplotlib
    output_path = OUTPUTS_DIR / "exercise1_output.png"
    save_comparison_grid(
        all_images,
        all_labels,
        output_path,
        title=f"DreamBooth Personalized Generation: '{SUBJECT_TOKEN} {CLASS_NAME}'",
        rows=3,
        cols=3,
        figsize=(15, 15)
    )

    # Also create a simple grid without labels
    simple_grid = create_image_grid(all_images, rows=3, cols=3, padding=4)
    simple_grid.save(OUTPUTS_DIR / "exercise1_grid_simple.png")

    # Print reflection questions
    print("\n" + "=" * 60)
    print("REFLECTION QUESTIONS")
    print("=" * 60)
    print("""
1. CONNECTION TO DDPM BASICS (Module 12.3.1):
   In Module 12.3.1, we trained a DDPM that generated random African fabric
   patterns without any control over what it produced. Now with DreamBooth:
   - How does adding text conditioning change what the model can do?
   - The U-Net architecture is essentially the same - what was fine-tuned?

2. THE SPECIAL TOKEN "sks":
   Notice that all prompts include the token "sks" (e.g., "sks african fabric").
   - Why do we need a special token instead of just saying "african fabric"?
   - What would happen if you removed "sks" from the prompt?
   - Try it! Generate with and without the token and compare results.

3. GENERALIZATION CAPABILITY:
   The model was trained on only ~10 fabric images, yet it can:
   - Put the fabric pattern on a dress
   - Render it as a watercolor painting
   - Apply it to a handbag
   How does the model "understand" these new contexts it never saw during training?

4. COMPARISON WITH DCGAN (Module 12.1.2):
   Both DCGAN and DreamBooth can generate African fabric patterns.
   - What can DreamBooth do that DCGAN cannot?
   - Which approach gives you more creative control?
   - Which would you use for different applications?

5. PRIOR PRESERVATION (Advanced):
   DreamBooth uses "prior preservation" during training to prevent forgetting.
   - What might happen if we didn't use prior preservation?
   - Why is this important for generative models?
    """)

    print("\n" + "=" * 60)
    print("WHAT TO DO NEXT")
    print("=" * 60)
    print("""
1. Examine the generated images in the 'outputs/' folder.

2. Experiment with prompts - edit GENERATION_PROMPTS at the top of this script:
   - Try different artistic styles (oil painting, sketch, 3D render)
   - Try different contexts (on furniture, as book cover, as tattoo)
   - Try combining with other concepts (anime style, vintage photo)

3. Try removing "sks" from a prompt and compare the output.

4. Proceed to Exercise 2 to explore generation parameters in depth.

5. Proceed to Exercise 3 to learn how to train your own DreamBooth model.
    """)

if __name__ == "__main__":
    main()
