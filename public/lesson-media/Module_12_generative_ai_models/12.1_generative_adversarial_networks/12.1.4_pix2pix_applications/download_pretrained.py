import os
import urllib.request
import zipfile
from pathlib import Path

# Configuration
MODEL_NAME = 'facades_label2photo'
WEIGHTS_URL = f'http://efrosgans.eecs.berkeley.edu/pix2pix/models-pytorch/{MODEL_NAME}.pth'

# Use script directory for paths (not current working directory)
SCRIPT_DIR = Path(__file__).parent.resolve()
CHECKPOINTS_DIR = SCRIPT_DIR / 'checkpoints'
WEIGHTS_FILENAME = 'facades_generator.pth'

def download_file(url, destination):
    """
    Download a file from URL with progress indicator.

    Args:
        url: Source URL
        destination: Local file path to save
    """
    print(f"Downloading from: {url}")
    print(f"Saving to: {destination}")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, downloaded * 100 / total_size)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rProgress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')

    urllib.request.urlretrieve(url, destination, progress_hook)
    print()  # New line after progress

def main():
    """Download the pre-trained facades model."""
    print("=" * 60)
    print("Downloading Pre-trained Pix2Pix Facades Model")
    print("=" * 60)
    print()

    # Create checkpoints directory
    CHECKPOINTS_DIR.mkdir(exist_ok=True)

    weights_path = CHECKPOINTS_DIR / WEIGHTS_FILENAME

    # Check if already downloaded
    if weights_path.exists():
        print(f"Weights already exist at: {weights_path}")
        print("Delete the file and run again to re-download.")
        return weights_path

    print(f"Model: {MODEL_NAME}")
    print(f"This model transforms facade labels into realistic building photos.")
    print()

    try:
        download_file(WEIGHTS_URL, weights_path)
        print()
        print("Download complete!")
        print(f"Weights saved to: {weights_path}")

        # Verify file size
        file_size = weights_path.stat().st_size / (1024 * 1024)
        print(f"File size: {file_size:.1f} MB")

        if file_size < 1:
            print("Warning: File seems too small. Download may have failed.")
            return None

    except Exception as e:
        print(f"\nError downloading weights: {e}")
        print()
        print("Alternative manual download:")
        print(f"1. Visit: {WEIGHTS_URL}")
        print(f"2. Save the file to: {weights_path}")
        return None

    print()
    print("Next steps:")
    print("  1. Run: python quick-start.py")
    print("  2. Run: python exercise1_observe.py")

    return weights_path

if __name__ == '__main__':
    main()
