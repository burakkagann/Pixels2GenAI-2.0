import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

from facades_generator import create_facades_generator

# Use script directory for paths (not current working directory)
SCRIPT_DIR = Path(__file__).parent.resolve()

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
    img_array = (img_array - 0.5) / 0.5  # Normalize to [-1, 1]

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
    img = (img + 1) / 2  # Denormalize to [0, 1]
    img = np.clip(img, 0, 1)
    return img

def main():
    """Generate a building facade from a segmentation label."""
    print("Pix2Pix Quick Start: Facades Demo")
    print("=" * 40)
    print()

    # Check for pre-trained weights
    weights_path = SCRIPT_DIR / 'checkpoints' / 'facades_generator.pth'

    if not weights_path.exists():
        print("Pre-trained weights not found!")
        print()
        print("Please run the download script first:")
        print("  python download_pretrained.py")
        print()
        print("This will download the facades_label2photo model.")
        return

    # Load generator with pre-trained weights
    print("Loading pre-trained facades generator...")
    generator = create_facades_generator(str(weights_path))
    generator.eval()
    print("Model loaded!")
    print()

    # Load sample facade label (CMP Facades dataset from Kaggle)
    sample_path = SCRIPT_DIR / 'sample_facades' / 'base' / 'cmp_b0001.png'

    if not sample_path.exists():
        print(f"Sample facade not found at: {sample_path}")
        print("Please download facade samples from:")
        print("  https://www.kaggle.com/datasets/adlteam/facade-dataset")
        print("And place them in sample_facades/base/")
        return

    label_img = Image.open(sample_path).convert('RGB')
    print(f"Input label: {sample_path}")

    # Preprocess and generate
    input_tensor = preprocess_image(label_img)

    with torch.no_grad():
        output_tensor = generator(input_tensor)

    # Postprocess
    generated_img = postprocess_image(output_tensor)
    label_display = np.array(label_img) / 255.0

    # Display result
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].imshow(label_display)
    axes[0].set_title('Input: Segmentation Label', fontweight='bold')
    axes[0].axis('off')

    axes[1].imshow(generated_img)
    axes[1].set_title('Output: Generated Facade', fontweight='bold')
    axes[1].axis('off')

    plt.suptitle('Pix2Pix: Label to Facade Translation', fontsize=14, fontweight='bold')
    plt.tight_layout()

    output_file = SCRIPT_DIR / 'quick_start_output.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"Output saved to: {output_file}")

    plt.show()

if __name__ == '__main__':
    main()
