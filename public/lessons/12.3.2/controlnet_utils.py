import numpy as np
from PIL import Image
from pathlib import Path

def load_image(image_path, size=512):
    """
    Load and preprocess an image for ControlNet.

    Parameters
    ----------
    image_path : str or Path
        Path to the input image.
    size : int
        Target size (images are resized to size x size).

    Returns
    -------
    tuple
        (PIL.Image, numpy.ndarray) - PIL Image and numpy array.
    """
    image = Image.open(image_path).convert('RGB')
    image = image.resize((size, size), Image.LANCZOS)
    return image, np.array(image)

def extract_canny_edges(image_array, low_threshold=100, high_threshold=200):
    """
    Extract Canny edges from an image using OpenCV.

    The Canny edge detector finds edges by looking for local maxima
    of the gradient of the image intensity. This creates sharp,
    well-defined edge maps ideal for structural control.

    Parameters
    ----------
    image_array : numpy.ndarray
        RGB image array (H, W, 3).
    low_threshold : int
        Lower threshold for hysteresis (default: 100).
    high_threshold : int
        Upper threshold for hysteresis (default: 200).

    Returns
    -------
    PIL.Image
        Canny edge image (grayscale converted to RGB for ControlNet).

    Reference
    ---------
    Canny, J. (1986). A computational approach to edge detection.
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 8(6), 679-698.
    """
    try:
        import cv2
    except ImportError:
        raise ImportError("OpenCV required. Install with: pip install opencv-python")

    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Apply Canny edge detection
    edges = cv2.Canny(gray, low_threshold, high_threshold)

    # Convert to 3-channel image for ControlNet
    edges_rgb = np.stack([edges, edges, edges], axis=-1)

    return Image.fromarray(edges_rgb)

def extract_lineart(image_array, sigma=1.0):
    """
    Extract clean line art from an image using edge-preserving filtering.

    This creates smoother, more artistic outlines compared to Canny edges.
    Useful for artistic applications where harsh edges are undesirable.

    Parameters
    ----------
    image_array : numpy.ndarray
        RGB image array (H, W, 3).
    sigma : float
        Gaussian blur sigma for smoothing (default: 1.0).

    Returns
    -------
    PIL.Image
        Line art image (white lines on black background).
    """
    try:
        import cv2
    except ImportError:
        raise ImportError("OpenCV required. Install with: pip install opencv-python")

    # Convert to grayscale
    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (0, 0), sigma)

    # Edge detection using Laplacian
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    laplacian = np.abs(laplacian)

    # Normalize to 0-255
    laplacian = (laplacian / laplacian.max() * 255).astype(np.uint8)

    # Threshold to create clean lines
    _, lines = cv2.threshold(laplacian, 20, 255, cv2.THRESH_BINARY)

    # Convert to 3-channel
    lines_rgb = np.stack([lines, lines, lines], axis=-1)

    return Image.fromarray(lines_rgb)

def create_comparison_grid(images, labels=None, title=None):
    """
    Create a side-by-side comparison grid of images.

    Parameters
    ----------
    images : list of PIL.Image
        List of images to display.
    labels : list of str, optional
        Labels for each image.
    title : str, optional
        Title for the grid.

    Returns
    -------
    PIL.Image
        Combined grid image.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib required. Install with: pip install matplotlib")

    from io import BytesIO

    n_images = len(images)

    # Create figure
    fig, axes = plt.subplots(1, n_images, figsize=(4 * n_images, 4), dpi=150)

    if n_images == 1:
        axes = [axes]

    for i, (ax, img) in enumerate(zip(axes, images)):
        ax.imshow(img)
        ax.axis('off')
        if labels and i < len(labels):
            ax.set_title(labels[i], fontsize=12, fontweight='bold')

    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    plt.tight_layout()

    # Convert to PIL Image using BytesIO buffer
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    grid_image = Image.open(buf).convert('RGB')
    plt.close(fig)

    return grid_image

def create_strength_sweep_grid(images, scales, prompt):
    """
    Create a grid showing different guidance strength values.

    Parameters
    ----------
    images : list of PIL.Image
        Generated images at different guidance scales.
    scales : list of float
        Guidance scale values used.
    prompt : str
        The prompt used for generation.

    Returns
    -------
    PIL.Image
        Grid showing guidance scale sweep.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib required. Install with: pip install matplotlib")

    from io import BytesIO

    n_images = len(images)
    cols = min(n_images, 5)
    rows = (n_images + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows + 0.5), dpi=150)

    if rows == 1:
        axes = [axes] if cols == 1 else axes.tolist()
    else:
        axes = axes.flatten().tolist()

    for i, (ax, img, scale) in enumerate(zip(axes, images, scales)):
        ax.imshow(img)
        ax.axis('off')
        ax.set_title(f'scale={scale}', fontsize=10)

    # Hide empty axes
    for i in range(len(images), len(axes)):
        axes[i].axis('off')

    fig.suptitle(f'Guidance Strength Sweep\nPrompt: "{prompt[:50]}..."' if len(prompt) > 50 else f'Guidance Strength Sweep\nPrompt: "{prompt}"',
                 fontsize=11, fontweight='bold')

    plt.tight_layout()

    # Convert to PIL Image using BytesIO buffer
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    buf.seek(0)
    grid_image = Image.open(buf).convert('RGB')
    plt.close(fig)

    return grid_image

def get_fabric_sample_paths(n_samples=4):
    """
    Get paths to sample African fabric images from the DCGAN module.

    Parameters
    ----------
    n_samples : int
        Number of sample images to return.

    Returns
    -------
    list of Path
        Paths to fabric images.
    """
    # Path to preprocessed African fabric dataset
    script_dir = Path(__file__).parent
    fabric_dir = script_dir.parent.parent / '12.1_generative_adversarial_networks' / '12.1.2_dcgan_art' / 'african_fabric_processed'

    if not fabric_dir.exists():
        # Try alternative path
        fabric_dir = script_dir.parent.parent / '12.1_generative_adversarial_networks' / '12.1.2_dcgan_art' / 'african_fabric_dataset'

    if not fabric_dir.exists():
        print(f"Warning: Fabric dataset not found at {fabric_dir}")
        return []

    # Get image files
    image_files = sorted(list(fabric_dir.glob('*.png')) + list(fabric_dir.glob('*.jpg')))

    if not image_files:
        print(f"Warning: No images found in {fabric_dir}")
        return []

    # Return requested number of samples
    step = max(1, len(image_files) // n_samples)
    return [image_files[i * step] for i in range(min(n_samples, len(image_files)))]

if __name__ == '__main__':
    # Test utilities
    print("Testing ControlNet utilities...")

    # Check for sample fabric images
    fabric_paths = get_fabric_sample_paths(4)

    if fabric_paths:
        print(f"Found {len(fabric_paths)} fabric samples")

        # Test edge extraction on first image
        image, array = load_image(fabric_paths[0], size=512)
        print(f"Loaded image: {image.size}")

        # Extract edges
        canny = extract_canny_edges(array)
        print(f"Canny edges: {canny.size}")

        # Extract line art
        lineart = extract_lineart(array)
        print(f"Line art: {lineart.size}")

        # Create comparison
        grid = create_comparison_grid(
            [image, canny, lineart],
            labels=['Original', 'Canny Edges', 'Line Art'],
            title='Control Signal Extraction'
        )
        grid.save('test_control_extraction.png')
        print("Saved test_control_extraction.png")
    else:
        print("No fabric samples found. Please ensure the African fabric dataset exists.")
