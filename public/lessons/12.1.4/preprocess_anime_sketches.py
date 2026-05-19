import os
from pathlib import Path
from PIL import Image
import numpy as np

# Configuration
INPUT_DIR = 'anime_sketch_dataset'       # Raw dataset folder
OUTPUT_DIR = 'anime_processed'           # Output folder for processed images
IMG_SIZE = 256                           # Target image size

def preprocess_dataset():
    """
    Process the Anime Sketch Colorization dataset.

    The original images are 512x256 (sketch|color side-by-side).
    We split them into separate 256x256 sketch and color images.
    """
    print("=" * 60)
    print("Preprocessing Anime Sketch Colorization Dataset")
    print("=" * 60)
    print()

    # Check input directory
    input_path = Path(INPUT_DIR)
    if not input_path.exists():
        print(f"Error: Input directory '{INPUT_DIR}' not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to: https://www.kaggle.com/datasets/ktaebum/anime-sketch-colorization-pair")
        print("2. Download the dataset (requires free Kaggle account)")
        print("3. Extract the ZIP file to create 'anime_sketch_dataset/' folder")
        print("4. The folder should contain 'train/' and optionally 'val/' subfolders")
        print("5. Run this script again")
        return

    # Create output directories
    output_path = Path(OUTPUT_DIR)
    sketch_dir = output_path / 'sketches'
    color_dir = output_path / 'colors'

    sketch_dir.mkdir(parents=True, exist_ok=True)
    color_dir.mkdir(parents=True, exist_ok=True)

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    image_files = []

    # Check for train subfolder (common Kaggle structure)
    train_path = input_path / 'train'
    if train_path.exists():
        for ext in image_extensions:
            image_files.extend(train_path.glob(f'*{ext}'))
    else:
        # Direct folder structure
        for ext in image_extensions:
            image_files.extend(input_path.glob(f'*{ext}'))

    image_files = sorted(image_files)

    if len(image_files) == 0:
        print(f"Error: No images found in '{INPUT_DIR}' or '{INPUT_DIR}/train/'")
        print("Please check your dataset extraction.")
        return

    print(f"Found {len(image_files)} images to process")
    print(f"Output directory: {OUTPUT_DIR}/")
    print()

    # Process images
    processed_count = 0
    skipped_count = 0

    for i, img_path in enumerate(image_files):
        try:
            # Load image
            img = Image.open(img_path).convert('RGB')
            width, height = img.size

            # Expected format: sketch on left, color on right
            # Total width should be 2x height (512x256)
            if width != 2 * height:
                # Try to handle different aspect ratios
                # Split in half regardless
                pass

            half_width = width // 2

            # Split into color (left) and sketch (right)
            # The Kaggle anime sketch colorization dataset has: color|sketch
            color_img = img.crop((0, 0, half_width, height))
            sketch_img = img.crop((half_width, 0, width, height))

            # Resize to target size
            sketch_img = sketch_img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
            color_img = color_img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)

            # Save processed images
            filename = f'{processed_count:05d}.png'
            sketch_img.save(sketch_dir / filename)
            color_img.save(color_dir / filename)

            processed_count += 1

            # Progress update
            if (i + 1) % 500 == 0:
                print(f"Processed {i + 1}/{len(image_files)} images...")

        except Exception as e:
            print(f"Warning: Skipped {img_path.name} - {e}")
            skipped_count += 1

    print()
    print("Preprocessing complete!")
    print(f"  Total images processed: {processed_count}")
    print(f"  Images skipped: {skipped_count}")
    print(f"  Output directory: {OUTPUT_DIR}/")
    print(f"  Sketch images: {OUTPUT_DIR}/sketches/")
    print(f"  Color images: {OUTPUT_DIR}/colors/")
    print(f"  Image size: {IMG_SIZE}x{IMG_SIZE}")

def extract_sample_sketches():
    """
    Extract a few sample sketches for testing exercises 1 and 2
    without requiring the full dataset.
    """
    output_path = Path(OUTPUT_DIR)
    sketch_dir = output_path / 'sketches'
    sample_dir = Path('sample_sketches')

    if not sketch_dir.exists():
        print("Note: Run preprocessing first to extract samples.")
        return

    sample_dir.mkdir(exist_ok=True)

    # Copy first 4 sketches as samples
    sketch_files = sorted(sketch_dir.glob('*.png'))[:4]

    if len(sketch_files) == 0:
        print("No processed sketches found.")
        return

    for i, src in enumerate(sketch_files):
        dst = sample_dir / f'sketch_{i+1:03d}.png'
        img = Image.open(src)
        img.save(dst)
        print(f"Extracted sample: {dst}")

    print(f"\nSample sketches saved to: {sample_dir}/")

def verify_dataset():
    """Verify the processed dataset is ready for training."""
    output_path = Path(OUTPUT_DIR)
    sketch_dir = output_path / 'sketches'
    color_dir = output_path / 'colors'

    print("\nDataset Verification:")
    print("-" * 40)

    if not output_path.exists():
        print("Status: NOT READY - Run preprocessing first")
        return False

    sketch_count = len(list(sketch_dir.glob('*.png')))
    color_count = len(list(color_dir.glob('*.png')))

    print(f"Sketch images: {sketch_count}")
    print(f"Color images:  {color_count}")

    if sketch_count == 0 or color_count == 0:
        print("Status: NOT READY - No images found")
        return False

    if sketch_count != color_count:
        print("Status: WARNING - Mismatched counts")
        return False

    # Check a sample image
    sample_sketch = next(sketch_dir.glob('*.png'))
    img = Image.open(sample_sketch)
    print(f"Image size: {img.size}")

    print("Status: READY for training")
    return True

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_dataset()
    elif len(sys.argv) > 1 and sys.argv[1] == '--samples':
        extract_sample_sketches()
    else:
        preprocess_dataset()
        print()
        verify_dataset()
        print()
        print("Next steps:")
        print("  1. Run: python exercise1_observe.py (uses pre-trained model)")
        print("  2. Run: python exercise3_train.py (trains your own model)")
