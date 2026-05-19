"""
Preprocess African Fabric Dataset for DCGAN Training

This script prepares the African fabric images from Kaggle for DCGAN training
by resizing them to 64x64 and ensuring consistent RGB format.

Dataset source: https://www.kaggle.com/datasets/mikuns/african-fabric
"""

import os
from PIL import Image
from pathlib import Path

def preprocess_african_fabric_dataset(
    input_dir='african_fabric_dataset',
    output_dir='african_fabric_processed',
    target_size=(64, 64)
):
    """
    Preprocess African fabric images for DCGAN training.

    Parameters:
        input_dir (str): Directory containing downloaded Kaggle dataset
        output_dir (str): Directory to save preprocessed images
        target_size (tuple): Target image dimensions (width, height)
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Get all image files
    input_path = Path(input_dir)
    image_files = list(input_path.glob('*.jpg')) + list(input_path.glob('*.png')) + list(input_path.glob('*.jpeg'))

    print(f"Found {len(image_files)} images in {input_dir}")

    if len(image_files) == 0:
        print(f"\nError: No images found in '{input_dir}'")
        print("Please ensure you have:")
        print("1. Downloaded the African fabric dataset from Kaggle")
        print("2. Extracted the ZIP file to the 'african_fabric_dataset/' directory")
        return

    # Process each image
    processed_count = 0
    skipped_count = 0

    for img_file in image_files:
        try:
            # Load image
            img = Image.open(img_file)

            # Convert to RGB (in case of RGBA or grayscale)
            img = img.convert('RGB')

            # Resize to target dimensions
            img_resized = img.resize(target_size, Image.LANCZOS)

            # Save preprocessed image
            output_filename = f'fabric_{processed_count:04d}.png'
            output_path = os.path.join(output_dir, output_filename)
            img_resized.save(output_path)

            processed_count += 1

            if processed_count % 50 == 0:
                print(f"Processed {processed_count} images...")

        except Exception as e:
            print(f"Error processing {img_file.name}: {e}")
            skipped_count += 1

    print(f"\nPreprocessing complete!")
    print(f"Total images processed: {processed_count}")
    print(f"Images skipped (errors): {skipped_count}")
    print(f"Output directory: {output_dir}")
    print(f"Image dimensions: {target_size[0]}×{target_size[1]} RGB")
    print(f"\nYou can now run exercise3_train.py to train the DCGAN on this dataset.")

if __name__ == '__main__':
    preprocess_african_fabric_dataset()
