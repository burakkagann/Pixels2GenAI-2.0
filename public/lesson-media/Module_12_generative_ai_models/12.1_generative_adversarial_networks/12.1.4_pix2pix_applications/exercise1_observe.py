import os
import torch
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from PIL import Image

from facades_generator import create_facades_generator

# Use script directory for paths (not current working directory)
SCRIPT_DIR = Path(__file__).parent.resolve()

def load_facade_labels(sample_dir=None, num_samples=4):
    """
    Load sample facade label images.

    Args:
        sample_dir: Directory containing sample label images
        num_samples: Number of labels to load

    Returns:
        List of PIL Image objects
    """
    if sample_dir is None:
        sample_path = SCRIPT_DIR / 'sample_facades' / 'base'
    else:
        sample_path = Path(sample_dir)

    if not sample_path.exists():
        print(f"Sample directory '{sample_path}' not found.")
        print("Please download facade samples from:")
        print("  https://www.kaggle.com/datasets/adlteam/facade-dataset")
        print("And place them in sample_facades/base/")
        return []

    # Find label images
    labels = []
    extensions = ['*.png', '*.jpg', '*.jpeg']

    for ext in extensions:
        labels.extend(sorted(sample_path.glob(ext)))

    if len(labels) == 0:
        print("No label images found. Please run create_sample_facades.py")
        return []

    # Load requested number
    loaded = []
    for i, path in enumerate(labels[:num_samples]):
        img = Image.open(path).convert('RGB')
        loaded.append(img)

    return loaded

def preprocess_image(img):
    """
    Prepare image for the generator.

    Args:
        img: PIL Image (256x256 RGB)

    Returns:
        Tensor of shape (1, 3, 256, 256) normalized to [-1, 1]
    """
    if img.size != (256, 256):
        img = img.resize((256, 256), Image.LANCZOS)

    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = (img_array - 0.5) / 0.5

    tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0)
    return tensor

def postprocess_image(tensor):
    """
    Convert generator output to displayable image.

    Args:
        tensor: Generator output (1, 3, 256, 256) in [-1, 1]

    Returns:
        numpy array (256, 256, 3) in [0, 1]
    """
    img = tensor.squeeze(0).permute(1, 2, 0).numpy()
    img = (img + 1) / 2
    img = np.clip(img, 0, 1)
    return img

def main():
    """Main exercise: observe Pix2Pix facade generation."""
    print("=" * 60)
    print("Exercise 1: Observe Pix2Pix Facade Generation")
    print("=" * 60)
    print()

    # Check for pre-trained weights
    weights_path = SCRIPT_DIR / 'checkpoints' / 'facades_generator.pth'

    if not weights_path.exists():
        print(f"Pre-trained weights not found at: {weights_path}")
        print()
        print("Please download the pre-trained model first:")
        print("  python download_pretrained.py")
        print()
        print("Running architecture test only...")

        from facades_generator import UnetGenerator
        generator = UnetGenerator(input_nc=3, output_nc=3, num_downs=8, ngf=64)
        total_params = sum(p.numel() for p in generator.parameters())
        print(f"\nGenerator Architecture:")
        print(f"  Type: U-Net with skip connections")
        print(f"  Input: 256x256 RGB segmentation label")
        print(f"  Output: 256x256 RGB building photo")
        print(f"  Parameters: {total_params:,}")
        return

    # Load pre-trained generator
    print("Loading pre-trained facades generator...")
    generator = create_facades_generator(str(weights_path))
    generator.eval()

    total_params = sum(p.numel() for p in generator.parameters())
    print("Generator loaded!")
    print()
    print("Generator Architecture:")
    print(f"  Type: U-Net with skip connections")
    print(f"  Input: 256x256 RGB segmentation label")
    print(f"  Output: 256x256 RGB building photo")
    print(f"  Parameters: {total_params:,}")
    print()

    # Load sample labels
    print("Loading sample facade labels...")
    labels = load_facade_labels(num_samples=4)

    if len(labels) == 0:
        print("No labels available. Exiting.")
        return

    print(f"Loaded {len(labels)} labels")
    print()

    # Generate facade images
    print("Generating building facades...")
    generated_images = []

    with torch.no_grad():
        for i, label in enumerate(labels):
            input_tensor = preprocess_image(label)
            output_tensor = generator(input_tensor)
            generated = postprocess_image(output_tensor)
            generated_images.append(generated)
            print(f"  Processed label {i+1}/{len(labels)}")

    # Create visualization
    print()
    print("Creating visualization...")

    num_samples = len(labels)
    fig, axes = plt.subplots(2, num_samples, figsize=(4*num_samples, 8))

    for i in range(num_samples):
        # Top row: input labels
        ax_label = axes[0, i] if num_samples > 1 else axes[0]
        label_array = np.array(labels[i]) / 255.0
        ax_label.imshow(label_array)
        ax_label.set_title(f'Label {i+1}', fontsize=12, fontweight='bold')
        ax_label.axis('off')

        # Bottom row: generated facades
        ax_gen = axes[1, i] if num_samples > 1 else axes[1]
        ax_gen.imshow(generated_images[i])
        ax_gen.set_title(f'Generated {i+1}', fontsize=12, fontweight='bold')
        ax_gen.axis('off')

    plt.suptitle('Pix2Pix: Segmentation Label to Building Facade',
                 fontsize=16, fontweight='bold')
    plt.tight_layout()

    # Save output
    output_file = SCRIPT_DIR / 'exercise1_output.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Saved output to: {output_file}")
    plt.show()

    # Print reflection questions
    print()
    print("=" * 60)
    print("Reflection Questions")
    print("=" * 60)
    print()
    print("1. How does Pix2Pix differ from DCGAN generation?")
    print("   - DCGAN: G(z) generates from random noise only")
    print("   - Pix2Pix: G(x) transforms an input image")
    print("   Think: Why is the input image essential for facade generation?")
    print()
    print("2. Why are skip connections essential?")
    print("   - Skip connections pass spatial details from encoder to decoder")
    print("   - Without them, fine details (edges, boundaries) would be lost")
    print("   Think: What would happen to window positions without skip connections?")
    print()
    print("3. What happens if you change the label colors?")
    print("   - The model learned specific color meanings from training data")
    print("   - Unusual colors may produce unexpected results")
    print("   - This demonstrates domain-specific learning")
    print()
    print("Exercise 1 complete!")

if __name__ == '__main__':
    main()
