import os
import torch
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

from facades_generator import create_facades_generator

# Use script directory for paths (not current working directory)
SCRIPT_DIR = Path(__file__).parent.resolve()

# Facade label colors (CMP Facades palette)
COLORS = {
    'background': (0, 0, 170),
    'wall': (128, 128, 128),
    'window': (170, 0, 0),
    'door': (255, 255, 0),
    'balcony': (0, 170, 0),
}

def load_generator():
    """Load the pre-trained facades generator."""
    weights_path = SCRIPT_DIR / 'checkpoints' / 'facades_generator.pth'

    if not weights_path.exists():
        print(f"Weights not found at: {weights_path}")
        print("Please run: python download_pretrained.py")
        return None

    generator = create_facades_generator(str(weights_path))
    generator.eval()
    return generator

def preprocess_image(img):
    """Convert PIL Image to model input tensor."""
    if img.size != (256, 256):
        img = img.resize((256, 256), Image.LANCZOS)

    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = (img_array - 0.5) / 0.5

    tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
    return tensor

def postprocess_image(tensor):
    """Convert model output to displayable image."""
    img = tensor.squeeze(0).permute(1, 2, 0).numpy()
    img = (img + 1) / 2
    img = np.clip(img, 0, 1)
    return img

def generate(generator, image):
    """Run generation on a single image."""
    with torch.no_grad():
        input_tensor = preprocess_image(image)
        output_tensor = generator(input_tensor)
        return postprocess_image(output_tensor)

def create_window_variations():
    """
    Create facade labels with different window arrangements.

    Returns:
        Dictionary with variation names and PIL Images
    """
    variations = {}
    size = 256

    # Few windows (sparse)
    img1 = Image.new('RGB', (size, size), COLORS['wall'])
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([0, 0, size, 30], fill=COLORS['background'])
    draw1.rectangle([50, 80, 100, 140], fill=COLORS['window'])
    draw1.rectangle([150, 80, 200, 140], fill=COLORS['window'])
    draw1.rectangle([100, 190, 155, 250], fill=COLORS['door'])
    variations['sparse'] = img1

    # Many windows (dense)
    img2 = Image.new('RGB', (size, size), COLORS['wall'])
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([0, 0, size, 25], fill=COLORS['background'])
    for row in range(4):
        for col in range(5):
            x = 15 + col * 48
            y = 35 + row * 50
            draw2.rectangle([x, y, x+35, y+40], fill=COLORS['window'])
    draw2.rectangle([108, 210, 148, 256], fill=COLORS['door'])
    variations['dense'] = img2

    # Asymmetric windows
    img3 = Image.new('RGB', (size, size), COLORS['wall'])
    draw3 = ImageDraw.Draw(img3)
    draw3.rectangle([0, 0, size, 30], fill=COLORS['background'])
    draw3.rectangle([20, 50, 80, 120], fill=COLORS['window'])
    draw3.rectangle([20, 140, 80, 190], fill=COLORS['window'])
    draw3.rectangle([150, 70, 230, 170], fill=COLORS['window'])  # Large window
    draw3.rectangle([100, 200, 155, 256], fill=COLORS['door'])
    variations['asymmetric'] = img3

    return variations

def create_partial_labels():
    """
    Create partial/incomplete facade labels.

    Returns:
        Dictionary with variation names and PIL Images
    """
    variations = {}
    size = 256

    # Load a base label (CMP Facades from Kaggle)
    base_path = SCRIPT_DIR / 'sample_facades' / 'base' / 'cmp_b0001.png'
    if base_path.exists():
        base = Image.open(base_path).convert('RGB')
    else:
        # Create simple base
        base = Image.new('RGB', (size, size), COLORS['wall'])
        draw = ImageDraw.Draw(base)
        draw.rectangle([0, 0, size, 30], fill=COLORS['background'])
        for col in range(3):
            x = 30 + col * 70
            draw.rectangle([x, 60, x+50, 120], fill=COLORS['window'])
            draw.rectangle([x, 140, x+50, 200], fill=COLORS['window'])
        draw.rectangle([100, 210, 155, 256], fill=COLORS['door'])

    variations['complete'] = base

    # Left half only
    left_half = base.copy()
    draw = ImageDraw.Draw(left_half)
    draw.rectangle([size//2, 0, size, size], fill=COLORS['wall'])
    variations['left_half'] = left_half

    # Center masked
    center_masked = base.copy()
    draw = ImageDraw.Draw(center_masked)
    margin = 60
    draw.rectangle([margin, margin, size-margin, size-margin], fill=COLORS['wall'])
    variations['center_masked'] = center_masked

    # Bottom only
    bottom_only = Image.new('RGB', (size, size), COLORS['wall'])
    bottom = base.crop((0, size//2, size, size))
    bottom_only.paste(bottom, (0, size//2))
    variations['bottom_only'] = bottom_only

    return variations

def create_color_variations():
    """
    Test how the model responds to unusual colors.

    Returns:
        Dictionary with variation names and PIL Images
    """
    variations = {}
    size = 256

    # Standard colors
    img1 = Image.new('RGB', (size, size), COLORS['wall'])
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([0, 0, size, 30], fill=COLORS['background'])
    for col in range(3):
        x = 30 + col * 70
        draw1.rectangle([x, 60, x+50, 130], fill=COLORS['window'])
    draw1.rectangle([100, 180, 155, 256], fill=COLORS['door'])
    variations['standard'] = img1

    # Inverted colors (swap window and wall)
    img2 = Image.new('RGB', (size, size), COLORS['window'])  # Wall is window color
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([0, 0, size, 30], fill=COLORS['background'])
    for col in range(3):
        x = 30 + col * 70
        draw2.rectangle([x, 60, x+50, 130], fill=COLORS['wall'])  # Windows are wall color
    draw2.rectangle([100, 180, 155, 256], fill=COLORS['balcony'])  # Door is green
    variations['inverted'] = img2

    # Random noise colors
    np.random.seed(42)
    noise = np.random.randint(0, 256, (size, size, 3), dtype=np.uint8)
    variations['noise'] = Image.fromarray(noise)

    # All one color (solid gray)
    variations['solid_gray'] = Image.new('RGB', (size, size), (128, 128, 128))

    return variations

def exploration_1_window_arrangements(generator):
    """Exploration 1: How do window arrangements affect output?"""
    print("\nExploration 1: Window Arrangement Variations")

    variations = create_window_variations()

    results = {}
    for name, label in variations.items():
        results[name] = generate(generator, label)
        print(f"  Generated: {name}")

    # Visualize
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    for i, (name, label) in enumerate(variations.items()):
        axes[0, i].imshow(np.array(label) / 255.0)
        axes[0, i].set_title(f'Label: {name.title()}', fontweight='bold')
        axes[0, i].axis('off')

        axes[1, i].imshow(results[name])
        axes[1, i].set_title('Generated', fontweight='bold')
        axes[1, i].axis('off')

    plt.suptitle('Effect of Window Arrangements', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_windows.png', dpi=150, bbox_inches='tight')
    print("  Saved: exercise2_windows.png")
    plt.close()

def exploration_2_partial_labels(generator):
    """Exploration 2: How does the model handle incomplete labels?"""
    print("\nExploration 2: Partial/Incomplete Labels")

    variations = create_partial_labels()

    results = {}
    for name, label in variations.items():
        results[name] = generate(generator, label)
        print(f"  Generated: {name}")

    # Visualize
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, (name, label) in enumerate(variations.items()):
        axes[0, i].imshow(np.array(label) / 255.0)
        axes[0, i].set_title(f'Label: {name.replace("_", " ").title()}', fontweight='bold')
        axes[0, i].axis('off')

        axes[1, i].imshow(results[name])
        axes[1, i].set_title('Generated', fontweight='bold')
        axes[1, i].axis('off')

    plt.suptitle('Effect of Incomplete Inputs', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_partial.png', dpi=150, bbox_inches='tight')
    print("  Saved: exercise2_partial.png")
    plt.close()

def exploration_3_color_semantics(generator):
    """Exploration 3: Do colors have learned semantic meaning?"""
    print("\nExploration 3: Color Semantic Testing")

    variations = create_color_variations()

    results = {}
    for name, label in variations.items():
        results[name] = generate(generator, label)
        print(f"  Generated: {name}")

    # Visualize
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i, (name, label) in enumerate(variations.items()):
        axes[0, i].imshow(np.array(label) / 255.0)
        axes[0, i].set_title(f'Input: {name.replace("_", " ").title()}', fontweight='bold')
        axes[0, i].axis('off')

        axes[1, i].imshow(results[name])
        axes[1, i].set_title('Generated', fontweight='bold')
        axes[1, i].axis('off')

    plt.suptitle('Color Semantics: What Has the Model Learned?', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_colors.png', dpi=150, bbox_inches='tight')
    print("  Saved: exercise2_colors.png")
    plt.close()

def exploration_4_consistency(generator):
    """Exploration 4: Is the model deterministic?"""
    print("\nExploration 4: Output Consistency Check")

    # Load a sample label (CMP Facades from Kaggle)
    sample_path = SCRIPT_DIR / 'sample_facades' / 'base' / 'cmp_b0001.png'
    if sample_path.exists():
        label = Image.open(sample_path).convert('RGB')
    else:
        # Create simple test label
        label = Image.new('RGB', (256, 256), COLORS['wall'])
        draw = ImageDraw.Draw(label)
        draw.rectangle([0, 0, 256, 30], fill=COLORS['background'])
        draw.rectangle([80, 80, 175, 150], fill=COLORS['window'])

    # Generate multiple times
    outputs = []
    for i in range(4):
        result = generate(generator, label)
        outputs.append(result)
        print(f"  Run {i+1}/4")

    # Check consistency
    consistent = True
    for i in range(1, len(outputs)):
        if not np.allclose(outputs[0], outputs[i]):
            consistent = False
            break

    # Visualize
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))

    for i in range(4):
        axes[0, i].imshow(np.array(label) / 255.0)
        axes[0, i].set_title(f'Input (Run {i+1})', fontweight='bold')
        axes[0, i].axis('off')

        axes[1, i].imshow(outputs[i])
        axes[1, i].set_title(f'Output (Run {i+1})', fontweight='bold')
        axes[1, i].axis('off')

    status = "IDENTICAL" if consistent else "DIFFERENT"
    plt.suptitle(f'Consistency Test: Outputs are {status}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(SCRIPT_DIR / 'exercise2_consistency.png', dpi=150, bbox_inches='tight')
    print(f"  Outputs are {status}")
    print("  Saved: exercise2_consistency.png")
    plt.close()

def main():
    """Main exploration exercise."""
    print("=" * 60)
    print("Exercise 2: Explore Pix2Pix Facade Model Behavior")
    print("=" * 60)

    # Load generator
    generator = load_generator()
    if generator is None:
        return

    print("Generator loaded!")

    # Run explorations
    exploration_1_window_arrangements(generator)
    exploration_2_partial_labels(generator)
    exploration_3_color_semantics(generator)
    exploration_4_consistency(generator)

    print()
    print("=" * 60)
    print("Try These Modifications")
    print("=" * 60)
    print()
    print("1. Create your own facade label:")
    print("   - Use a drawing program with the color palette")
    print("   - Save as PNG at 256x256 resolution")
    print("   - Run exercise1_observe.py with your custom label")
    print()
    print("2. Experiment with architectural styles:")
    print("   - Try different window-to-wall ratios")
    print("   - Add balconies (green color)")
    print("   - Create asymmetric designs")
    print()
    print("3. Test edge cases:")
    print("   - All windows, no walls")
    print("   - Gradients instead of solid colors")
    print("   - Mix colors from different domains")
    print()
    print("Output files created:")
    print("  - exercise2_windows.png")
    print("  - exercise2_partial.png")
    print("  - exercise2_colors.png")
    print("  - exercise2_consistency.png")
    print()
    print("Exercise 2 complete!")

if __name__ == '__main__':
    main()
