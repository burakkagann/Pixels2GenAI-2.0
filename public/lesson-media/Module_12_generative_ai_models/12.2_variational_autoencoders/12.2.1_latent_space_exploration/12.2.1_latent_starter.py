import numpy as np
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# Configuration
IMAGE_SIZE = 16
INPUT_DIM = IMAGE_SIZE * IMAGE_SIZE
HIDDEN_DIM = 128
LATENT_DIM = 8

class SimpleVAE(nn.Module):
    """
    A simplified VAE for the interpolation exercise.

    You need to implement:
    - encode(): Map input to latent space mean
    - decode(): Reconstruct from latent vector
    """

    def __init__(self):
        super().__init__()

        # Encoder layers
        self.encoder_fc1 = nn.Linear(INPUT_DIM, HIDDEN_DIM)
        self.encoder_fc2 = nn.Linear(HIDDEN_DIM, HIDDEN_DIM)
        self.fc_mu = nn.Linear(HIDDEN_DIM, LATENT_DIM)

        # Decoder layers
        self.decoder_fc1 = nn.Linear(LATENT_DIM, HIDDEN_DIM)
        self.decoder_fc2 = nn.Linear(HIDDEN_DIM, HIDDEN_DIM)
        self.decoder_out = nn.Linear(HIDDEN_DIM, INPUT_DIM)

    def encode(self, x):
        """
        Encode input to latent space.

        TODO: Implement the encoding process
        1. Pass x through encoder_fc1 and apply ReLU
        2. Pass result through encoder_fc2 and apply ReLU
        3. Pass result through fc_mu to get latent mean

        Args:
            x: Input tensor of shape (batch_size, INPUT_DIM)

        Returns:
            mu: Latent mean of shape (batch_size, LATENT_DIM)
        """
        # TODO: Your implementation here
        # h = ...
        # h = ...
        # mu = ...
        # return mu
        pass

    def decode(self, z):
        """
        Decode latent vector to reconstructed image.

        TODO: Implement the decoding process
        1. Pass z through decoder_fc1 and apply ReLU
        2. Pass result through decoder_fc2 and apply ReLU
        3. Pass result through decoder_out
        4. Apply Sigmoid to get values in [0, 1]

        Args:
            z: Latent vector of shape (batch_size, LATENT_DIM)

        Returns:
            recon: Reconstructed image of shape (batch_size, INPUT_DIM)
        """
        # TODO: Your implementation here
        # h = ...
        # h = ...
        # out = ...
        # return torch.sigmoid(out)
        pass

def interpolate(vae, pattern_a, pattern_b, num_steps=8):
    """
    Interpolate between two patterns in latent space.

    TODO: Implement latent space interpolation
    1. Encode both patterns to get their latent representations
    2. For each step, compute interpolated latent vector: z = (1-alpha)*z_a + alpha*z_b
    3. Decode each interpolated latent vector
    4. Return list of decoded images

    Args:
        vae: Trained VAE model
        pattern_a: First pattern tensor of shape (1, INPUT_DIM)
        pattern_b: Second pattern tensor of shape (1, INPUT_DIM)
        num_steps: Number of interpolation steps

    Returns:
        interpolated: List of numpy arrays, each of shape (IMAGE_SIZE, IMAGE_SIZE)
    """
    vae.eval()
    interpolated = []

    with torch.no_grad():
        # TODO: Step 1 - Encode both patterns
        # z_a = vae.encode(...)
        # z_b = vae.encode(...)

        # TODO: Step 2 - Create interpolation alphas from 0 to 1
        # alphas = np.linspace(...)

        # TODO: Step 3 - For each alpha, interpolate and decode
        # for alpha in alphas:
        #     z = (1 - alpha) * z_a + alpha * z_b
        #     decoded = vae.decode(z)
        #     interpolated.append(decoded.numpy().reshape(IMAGE_SIZE, IMAGE_SIZE))

        pass  # Remove this when you implement the function

    return interpolated

def create_test_patterns():
    """Create two test patterns for interpolation."""
    # Pattern A: Horizontal line
    pattern_a = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float32)
    mid = IMAGE_SIZE // 2
    pattern_a[mid - 1:mid + 1, :] = 1.0

    # Pattern B: Vertical line
    pattern_b = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.float32)
    pattern_b[:, mid - 1:mid + 1] = 1.0

    return (
        torch.tensor(pattern_a.flatten()).unsqueeze(0),
        torch.tensor(pattern_b.flatten()).unsqueeze(0)
    )

def visualize_interpolation(images, save_path='my_interpolation.png'):
    """Visualize the interpolation sequence."""
    num_images = len(images)
    fig, axes = plt.subplots(1, num_images, figsize=(num_images * 2, 2), dpi=150)

    for i, img in enumerate(images):
        axes[i].imshow(img, cmap='gray', vmin=0, vmax=1)
        axes[i].axis('off')
        alpha = i / (num_images - 1)
        axes[i].set_title(f'a={alpha:.2f}', fontsize=8)

    plt.suptitle('Latent Space Interpolation', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")

def main():
    """Test your implementation."""
    print("Creating VAE model...")
    vae = SimpleVAE()

    # Note: In a real scenario, you would load pre-trained weights here
    # For testing, we use random weights (results will be noisy)

    print("Creating test patterns...")
    pattern_a, pattern_b = create_test_patterns()

    print("Performing interpolation...")
    interpolated = interpolate(vae, pattern_a, pattern_b, num_steps=8)

    if interpolated:
        print("Visualizing results...")
        visualize_interpolation(interpolated)
        print("Done! Check my_interpolation.png")
    else:
        print("Interpolation returned empty list. Check your implementation!")

if __name__ == "__main__":
    main()
