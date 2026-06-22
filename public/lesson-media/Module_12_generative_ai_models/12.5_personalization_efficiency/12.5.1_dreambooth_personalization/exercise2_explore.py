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
# Configuration
# =============================================================================

SUBJECT_TOKEN = "sks"
CLASS_NAME = "african fabric pattern"
LORA_PATH = MODELS_DIR / "fabric_lora"

# Base prompt for experiments
BASE_PROMPT = f"a beautiful {SUBJECT_TOKEN} {CLASS_NAME}, detailed texture, vibrant colors"

# =============================================================================
# Part A: Guidance Scale Comparison
# =============================================================================

def part_a_guidance_scale(pipe, device):
    """
    Compare generation results across different guidance scales.

    Guidance scale (classifier-free guidance) controls how strongly the model
    follows the text prompt:
    - Low (1-3): More creative/random, may ignore prompt
    - Medium (7-8): Good balance (default)
    - High (12-20): Strict adherence, may look artificial

    This is similar to how DDPM sampling works (Module 12.3.1), but with
    an additional term that pushes the generation toward the prompt.
    """
    print_section_header("Part A: Guidance Scale Comparison")

    guidance_scales = [1.5, 3.0, 7.5, 12.0, 20.0]
    seed = 42

    images = []
    labels = []

    for scale in guidance_scales:
        print(f"\nGenerating with guidance_scale = {scale}")

        result = generate_images(
            pipe,
            BASE_PROMPT,
            num_inference_steps=30,
            guidance_scale=scale,
            seed=seed,
            device=device
        )

        images.extend(result)
        labels.append(f"Scale: {scale}")

    # Save comparison
    output_path = OUTPUTS_DIR / "exercise2_guidance_comparison.png"
    save_comparison_grid(
        images,
        labels,
        output_path,
        title="Guidance Scale Comparison\n(Same prompt, same seed, different guidance)",
        rows=1,
        cols=5,
        figsize=(20, 5)
    )

    print("\n" + "-" * 50)
    print("INTERPRETATION:")
    print("-" * 50)
    print("""
- Scale 1.5: Very low guidance - more random, creative, may deviate from prompt
- Scale 3.0: Low guidance - some prompt influence, high diversity
- Scale 7.5: Default - good balance between quality and prompt adherence
- Scale 12.0: High guidance - strong prompt following, less diversity
- Scale 20.0: Very high - extremely strict, may look artificial or saturated

For African fabric patterns:
- Lower guidance may produce more abstract interpretations
- Higher guidance emphasizes the learned texture and colors more strongly
    """)

    return images

# =============================================================================
# Part B: Style Transfer Grid
# =============================================================================

def part_b_style_grid(pipe, device):
    """
    Generate the personalized subject in 9 different artistic styles.

    This demonstrates that DreamBooth preserves the subject's identity
    while allowing stylistic variations through prompt engineering.
    """
    print_section_header("Part B: Style Transfer Grid")

    styles = [
        ("Photorealistic", f"professional photograph of {SUBJECT_TOKEN} {CLASS_NAME}, studio lighting, high detail"),
        ("Oil Painting", f"oil painting of {SUBJECT_TOKEN} {CLASS_NAME}, impressionist style, brush strokes visible"),
        ("Watercolor", f"watercolor painting of {SUBJECT_TOKEN} {CLASS_NAME}, soft edges, paper texture"),
        ("Anime", f"{SUBJECT_TOKEN} {CLASS_NAME} in anime style, cel shading, vibrant"),
        ("Cyberpunk", f"{SUBJECT_TOKEN} {CLASS_NAME} cyberpunk style, neon colors, futuristic"),
        ("Vintage", f"vintage photograph of {SUBJECT_TOKEN} {CLASS_NAME}, 1970s aesthetic, faded colors"),
        ("Minimalist", f"minimalist design inspired by {SUBJECT_TOKEN} {CLASS_NAME}, simple shapes, clean"),
        ("Psychedelic", f"psychedelic art featuring {SUBJECT_TOKEN} {CLASS_NAME}, trippy colors, swirling"),
        ("Line Art", f"detailed line drawing of {SUBJECT_TOKEN} {CLASS_NAME}, black and white, intricate"),
    ]

    images = []
    labels = []
    seed = 123

    for style_name, prompt in styles:
        print(f"\nGenerating: {style_name}")

        result = generate_images(
            pipe,
            prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            seed=seed,
            device=device
        )

        images.extend(result)
        labels.append(style_name)

    # Save grid
    output_path = OUTPUTS_DIR / "exercise2_style_grid.png"
    save_comparison_grid(
        images,
        labels,
        output_path,
        title=f"Style Transfer: '{SUBJECT_TOKEN} {CLASS_NAME}' in 9 Artistic Styles",
        rows=3,
        cols=3,
        figsize=(15, 15)
    )

    print("\n" + "-" * 50)
    print("INTERPRETATION:")
    print("-" * 50)
    print("""
Notice how the core fabric pattern characteristics are preserved across styles:
- Color palette tendencies (if trained on vibrant patterns)
- Geometric motifs and shapes
- Overall "feel" of the learned concept

This demonstrates that DreamBooth encodes the ESSENCE of the subject,
not just pixel-level copying. The model understands what makes these
patterns distinctively African fabric.

Compare to Module 12.1.2 (DCGAN): DCGAN could only generate one "style"
of fabric. DreamBooth + text conditioning gives you infinite style variations.
    """)

    return images

# =============================================================================
# Part C: Seed Variation Study
# =============================================================================

def part_c_seed_variation(pipe, device):
    """
    Generate multiple images with different seeds to study diversity.

    This helps understand:
    - How much variation exists within the learned concept
    - Whether the model has memorized training images (overfitting)
    - The diversity-quality trade-off
    """
    print_section_header("Part C: Seed Variation Study")

    prompt = f"a {SUBJECT_TOKEN} {CLASS_NAME}, beautiful colors, detailed"
    seeds = [1, 42, 100, 256, 512, 777, 999, 1234, 2048]

    images = []
    labels = []

    for seed in seeds:
        print(f"\nGenerating with seed = {seed}")

        result = generate_images(
            pipe,
            prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            seed=seed,
            device=device
        )

        images.extend(result)
        labels.append(f"Seed: {seed}")

    # Save grid
    output_path = OUTPUTS_DIR / "exercise2_seed_comparison.png"
    save_comparison_grid(
        images,
        labels,
        output_path,
        title="Seed Variation: Same Prompt, Different Random Seeds",
        rows=3,
        cols=3,
        figsize=(15, 15)
    )

    print("\n" + "-" * 50)
    print("INTERPRETATION:")
    print("-" * 50)
    print("""
What to look for:

1. DIVERSITY: Are the patterns sufficiently different?
   - Good: Various colors, layouts, and motifs
   - Bad: All look nearly identical (potential overfitting)

2. CONSISTENCY: Do they all clearly represent African fabric?
   - Good: All recognizable as the learned concept
   - Bad: Some look like random patterns or other styles

3. QUALITY: Is quality consistent across seeds?
   - Good: All images are high quality
   - Bad: Some seeds produce artifacts or degraded outputs

If all images look too similar, the model may have overfit to the
training images. This is common with very small training sets (<5 images).
Prior preservation helps prevent this (see Exercise 3).
    """)

    return images

# =============================================================================
# Main Script
# =============================================================================

def main():
    """Run all exploration experiments."""

    print_section_header("Exercise 2: Explore Generation Parameters")

    # Setup
    device = get_device()
    print(f"\nDevice: {device}")
    if device == "cuda":
        check_gpu_memory()

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load model
    print("\n" + "=" * 50)
    print("Loading Model")
    print("=" * 50)

    pipe = load_base_pipeline(
        use_fp16=(device == "cuda"),
        use_fast_scheduler=True
    )
    pipe = load_lora_weights(pipe, LORA_PATH)

    # Run experiments
    print("\n")
    part_a_images = part_a_guidance_scale(pipe, device)

    print("\n")
    part_b_images = part_b_style_grid(pipe, device)

    print("\n")
    part_c_images = part_c_seed_variation(pipe, device)

    # Summary
    print("\n" + "=" * 60)
    print("EXERCISE 2 COMPLETE")
    print("=" * 60)
    print(f"""
Generated outputs saved to: {OUTPUTS_DIR}

Files created:
- exercise2_guidance_comparison.png (Part A)
- exercise2_style_grid.png (Part B)
- exercise2_seed_comparison.png (Part C)

MODIFICATION CHALLENGES:
------------------------

1. CREATE A "FABRIC IN NATURE" GRID:
   Edit Part B to generate the fabric pattern in natural contexts:
   - Forest background
   - Beach scene
   - Mountain landscape
   - Garden setting
   - Underwater scene
   - Desert environment
   - Snow scene
   - Sunset backdrop
   - Rain/storm scene

2. FIND YOUR OPTIMAL GUIDANCE SCALE:
   Many artists have a preferred guidance scale. Experiment with values
   between 5-12 and find what produces results you like best.

3. CREATE A PROMPT COMPARISON:
   Generate the same seed with different prompt variations:
   - Short prompt: "sks african fabric"
   - Medium prompt: "beautiful sks african fabric pattern"
   - Long prompt: "highly detailed sks african fabric pattern with intricate
     geometric designs, vibrant traditional colors, professional photograph"

4. NEGATIVE PROMPTS (Advanced):
   Try adding negative prompts to remove unwanted elements:
   pipe(..., negative_prompt="blurry, low quality, distorted")

NEXT STEPS:
-----------
Proceed to Exercise 3 to learn how to train your own DreamBooth model
and understand the training process in detail.
    """)

# =============================================================================
# Alternative: Run Individual Parts
# =============================================================================

def run_part(part_name):
    """Run a single part of the exercise."""
    device = get_device()
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    pipe = load_base_pipeline(use_fp16=(device == "cuda"))
    pipe = load_lora_weights(pipe, LORA_PATH)

    if part_name.lower() == 'a':
        part_a_guidance_scale(pipe, device)
    elif part_name.lower() == 'b':
        part_b_style_grid(pipe, device)
    elif part_name.lower() == 'c':
        part_c_seed_variation(pipe, device)
    else:
        print(f"Unknown part: {part_name}")
        print("Valid options: a, b, c")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Exercise 2: Explore Generation Parameters')
    parser.add_argument('--part', type=str, default=None,
                        help='Run specific part (a, b, or c). Default: run all.')
    args = parser.parse_args()

    if args.part:
        run_part(args.part)
    else:
        main()
