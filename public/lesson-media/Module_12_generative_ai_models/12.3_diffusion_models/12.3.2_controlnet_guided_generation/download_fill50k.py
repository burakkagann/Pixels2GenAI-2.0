import os
import json
from pathlib import Path
from tqdm import tqdm
import zipfile
import requests

# Script configuration
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / 'fill50k'

# Dataset URL (hosted on Hugging Face)
DATASET_URL = "https://huggingface.co/lllyasviel/ControlNet/resolve/main/training/fill50k.zip"

def download_with_progress(url, output_path, description="Downloading"):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(output_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=description) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

def create_synthetic_fill50k(num_samples=1000):
    """
    Create a synthetic Fill50K-style dataset for demonstration.

    If the official dataset is unavailable, this creates a smaller
    synthetic version with the same format for testing purposes.
    """
    import numpy as np
    from PIL import Image, ImageDraw

    print(f"Creating synthetic Fill50K dataset ({num_samples} samples)...")

    source_dir = OUTPUT_DIR / 'source'
    target_dir = OUTPUT_DIR / 'target'
    source_dir.mkdir(parents=True, exist_ok=True)
    target_dir.mkdir(parents=True, exist_ok=True)

    metadata = []
    np.random.seed(42)

    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
    ]

    for i in tqdm(range(num_samples), desc="Generating samples"):
        # Image size
        size = 512

        # Random circle parameters
        cx = np.random.randint(100, size - 100)
        cy = np.random.randint(100, size - 100)
        radius = np.random.randint(50, 150)

        # Random fill color
        color = colors[i % len(colors)]

        # Create source (outline only)
        source_img = Image.new('RGB', (size, size), (255, 255, 255))
        draw_source = ImageDraw.Draw(source_img)
        draw_source.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(0, 0, 0),
            width=3
        )

        # Create target (filled)
        target_img = Image.new('RGB', (size, size), (255, 255, 255))
        draw_target = ImageDraw.Draw(target_img)
        draw_target.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=color,
            outline=(0, 0, 0),
            width=3
        )

        # Save images
        source_path = f'{i}.png'
        target_path = f'{i}.png'
        source_img.save(source_dir / source_path)
        target_img.save(target_dir / target_path)

        # Create prompt
        color_name = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'orange', 'purple'][i % 8]
        prompt = f"a {color_name} filled circle"

        metadata.append({
            'source': source_path,
            'target': target_path,
            'prompt': prompt
        })

    # Save metadata
    with open(OUTPUT_DIR / 'prompt.json', 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Dataset created at: {OUTPUT_DIR}")
    print(f"  - {num_samples} source images")
    print(f"  - {num_samples} target images")
    print(f"  - prompt.json metadata file")

def main():
    print("=" * 60)
    print("Fill50K Dataset Download")
    print("=" * 60)
    print()

    if OUTPUT_DIR.exists() and (OUTPUT_DIR / 'prompt.json').exists():
        print(f"Dataset already exists at: {OUTPUT_DIR}")
        response = input("Re-download? (y/n): ")
        if response.lower() != 'y':
            return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Attempting to download official Fill50K dataset...")
    print(f"URL: {DATASET_URL}")
    print()

    zip_path = OUTPUT_DIR / 'fill50k.zip'

    try:
        # Try to download official dataset
        download_with_progress(DATASET_URL, zip_path, "Downloading Fill50K")

        # Extract
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)

        # Handle nested directory structure (zip contains fill50k/ folder)
        nested_dir = OUTPUT_DIR / 'fill50k'
        if nested_dir.exists() and nested_dir.is_dir():
            print("Fixing nested directory structure...")
            import shutil
            # Move contents from nested directory to parent
            for item in nested_dir.iterdir():
                dest = OUTPUT_DIR / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(OUTPUT_DIR))
            # Remove empty nested directory
            nested_dir.rmdir()

        # Clean up zip file
        zip_path.unlink()
        print()
        print("Download complete!")

    except Exception as e:
        print(f"Download failed: {e}")
        print()
        print("Creating synthetic dataset instead...")
        print("(This is smaller but demonstrates the same training mechanism)")
        print()

        # Create synthetic dataset
        create_synthetic_fill50k(num_samples=1000)

    # Verify
    print()
    print("Verifying dataset...")

    if (OUTPUT_DIR / 'prompt.json').exists():
        with open(OUTPUT_DIR / 'prompt.json', 'r') as f:
            metadata = json.load(f)
        print(f"  Found {len(metadata)} samples")

        source_count = len(list((OUTPUT_DIR / 'source').glob('*.png')))
        target_count = len(list((OUTPUT_DIR / 'target').glob('*.png')))
        print(f"  Source images: {source_count}")
        print(f"  Target images: {target_count}")

        print()
        print("Dataset ready for training!")
    else:
        print("Error: Dataset verification failed")

if __name__ == '__main__':
    main()
