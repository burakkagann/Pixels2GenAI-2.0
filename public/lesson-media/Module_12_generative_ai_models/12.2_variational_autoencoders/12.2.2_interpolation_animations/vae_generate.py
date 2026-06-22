import torch
import matplotlib.pyplot as plt
import numpy as np

from vae_model import VAE, LATENT_DIM

def load_pretrained_vae(weights_path='vae_weights.pth'):
    """
    Load a pre-trained VAE model.

    Args:
        weights_path: Path to the saved weights file

    Returns:
        Loaded VAE model in evaluation mode
    """
    vae = VAE(latent_dim=LATENT_DIM)

    try:
        vae.load_state_dict(torch.load(weights_path, map_location='cpu'))
        print(f"Loaded pre-trained weights from {weights_path}")
    except FileNotFoundError:
        print(f"Warning: {weights_path} not found. Using random weights.")
        print("Run 'python vae_train.py' first to train the model.")

    vae.eval()
    return vae

def generate_samples(vae, num_samples=16, seed=None):
    """
    Generate random samples from the VAE.

    Args:
        vae: Trained VAE model
        num_samples: Number of images to generate
        seed: Random seed for reproducibility (optional)

    Returns:
        Generated images as numpy array (num_samples, H, W, 3)
    """
    if seed is not None:
        torch.manual_seed(seed)

    # Sample from prior (standard normal)
    z = torch.randn(num_samples, LATENT_DIM)

    # Decode to images
    with torch.no_grad():
        images = vae.decoder(z)

    # Convert to displayable format
    images = (images + 1) / 2  # [-1, 1] -> [0, 1]
    images = images.clamp(0, 1)
    images = images.permute(0, 2, 3, 1).numpy()  # NCHW -> NHWC

    return images

def display_samples(images, title="VAE Generated Samples"):
    """
    Display a grid of generated images.

    Args:
        images: Array of images (N, H, W, 3)
        title: Title for the figure
    """
    n = int(np.ceil(np.sqrt(len(images))))
    fig, axes = plt.subplots(n, n, figsize=(n * 2.5, n * 2.5))

    for i, ax in enumerate(axes.flat):
        if i < len(images):
            ax.imshow(images[i])
        ax.axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

def main():
    """Generate and save a grid of VAE samples."""
    print("=" * 50)
    print("VAE Sample Generation")
    print("=" * 50)

    # Load model
    vae = load_pretrained_vae()

    # Generate samples
    print("\nGenerating 16 random samples...")
    images = generate_samples(vae, num_samples=16, seed=42)

    # Display and save
    fig = display_samples(images, "VAE Generated Abstract Art")
    fig.savefig('generated_samples.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Saved generated_samples.png")

    # Generate individual samples
    print("\nGenerating 4 individual samples...")
    single_images = generate_samples(vae, num_samples=4, seed=123)

    for i, img in enumerate(single_images):
        plt.figure(figsize=(4, 4))
        plt.imshow(img)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(f'sample_{i+1}.png', dpi=150, bbox_inches='tight',
                    facecolor='white')
        plt.close()
        print(f"Saved sample_{i+1}.png")

    print("\nDone! Check the generated files.")

if __name__ == '__main__':
    main()
