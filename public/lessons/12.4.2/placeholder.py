# =============================================================================
# IMPLEMENTATION SPECIFICATIONS
# =============================================================================

"""
KEY COMPONENTS TO IMPLEMENT:

1. Encoder Network
   - CNN that maps input image to continuous latent z_e
   - Input: (batch, 3, 256, 256)
   - Output: (batch, embedding_dim, 32, 32)
   - Downsampling factor: 8x

2. Vector Quantizer Layer (CORE COMPONENT)
   class VectorQuantizer(nn.Module):
       def __init__(self, num_embeddings=512, embedding_dim=256, commitment_cost=0.25):
           self.embedding = nn.Embedding(num_embeddings, embedding_dim)
           self.commitment_cost = commitment_cost

       def forward(self, z_e):
           # z_e: (batch, embedding_dim, height, width)
           # Flatten spatial dims
           # Compute distances to all codebook entries
           # Find nearest entry (argmin)
           # Apply straight-through estimator
           # Compute losses
           return z_q, vq_loss, encoding_indices

3. Decoder Network
   - CNN that reconstructs image from quantized latent z_q
   - Input: (batch, embedding_dim, 32, 32)
   - Output: (batch, 3, 256, 256)
   - Upsampling factor: 8x

4. Loss Functions
   - Reconstruction loss: F.mse_loss(x, x_recon)
   - VQ loss (codebook): ||sg[z_e] - z_q||^2
   - Commitment loss: beta * ||z_e - sg[z_q]||^2
   - (VQGAN) Discriminator loss: adversarial loss
   - (VQGAN) Perceptual loss: VGG feature matching

5. Straight-Through Estimator
   # Forward: use z_q
   # Backward: copy gradients to z_e
   z_q = z_e + (z_q - z_e).detach()  # Trick!

SUGGESTED FILE STRUCTURE:
- simple_vqvae.py: Minimal VQ-VAE on MNIST
- vqvae_solution.py: Full implementation on fabrics
- vqvae_starter.py: Template for students
- vqgan_solution.py: With discriminator and perceptual loss
- codebook_analysis.py: Visualize and analyze codebook
"""

# =============================================================================
# ARCHITECTURE DETAILS
# =============================================================================

ENCODER_ARCHITECTURE = """
Conv2d(3, 64, 4, stride=2, padding=1)    # 256 -> 128
ReLU + BatchNorm
Conv2d(64, 128, 4, stride=2, padding=1)  # 128 -> 64
ReLU + BatchNorm
Conv2d(128, 256, 4, stride=2, padding=1) # 64 -> 32
ReLU + BatchNorm
Conv2d(256, embedding_dim, 3, padding=1) # 32 -> 32 (no downsampling)
"""

DECODER_ARCHITECTURE = """
Conv2d(embedding_dim, 256, 3, padding=1) # 32 -> 32
ReLU + BatchNorm
ConvTranspose2d(256, 128, 4, stride=2, padding=1)  # 32 -> 64
ReLU + BatchNorm
ConvTranspose2d(128, 64, 4, stride=2, padding=1)   # 64 -> 128
ReLU + BatchNorm
ConvTranspose2d(64, 3, 4, stride=2, padding=1)     # 128 -> 256
Tanh
"""

# =============================================================================
# EXPECTED OUTPUTS
# =============================================================================

"""
OUTPUT FILES TO GENERATE:

1. vqvae_reconstructions.png
   - Grid showing original vs reconstructed images

2. codebook_usage.png
   - Histogram of how often each codebook entry is used
   - Ideal: uniform distribution, no dead codes

3. codebook_visualization.png
   - Decode each codebook entry to see what it represents
   - May need to tile spatial positions

4. reconstruction_comparison.png
   - Side-by-side: VAE | VQ-VAE | VQGAN reconstructions

5. token_sequence.png
   - Show image as grid of token indices (32x32 integers)
   - Color-coded by codebook entry

6. training_progress.gif
   - Reconstruction quality over training epochs

7. perplexity_plot.png
   - Codebook perplexity over training (measure of utilization)
"""

# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

VQ_VAE_CONFIG = {
    "image_size": 256,
    "num_embeddings": 512,       # Codebook size (K)
    "embedding_dim": 256,        # Codebook vector dimension (D)
    "commitment_cost": 0.25,     # Beta in commitment loss
    "learning_rate": 3e-4,
    "batch_size": 32,
    "epochs": 100,
    "downsampling_factor": 8,    # Latent spatial size = 256/8 = 32
}

VQGAN_CONFIG = {
    **VQ_VAE_CONFIG,
    "discriminator_start_epoch": 10,
    "perceptual_loss_weight": 0.1,
    "adversarial_loss_weight": 0.1,
    "discriminator_lr": 4e-4,
}

# =============================================================================
# RESOURCES
# =============================================================================

"""
PAPERS:
- VQ-VAE: https://arxiv.org/abs/1711.00937
- VQ-VAE-2: https://arxiv.org/abs/1906.00446
- VQGAN: https://arxiv.org/abs/2012.09841
- Open-MAGVIT2: https://arxiv.org/abs/2409.04410

TUTORIALS:
- Keras VQ-VAE: https://keras.io/examples/generative/vq_vae/
- ML Berkeley Explained: https://mlberkeley.substack.com/p/vq-vae

GITHUB:
- CompVis Taming Transformers: https://github.com/CompVis/taming-transformers
- lucidrains vector-quantize-pytorch: https://github.com/lucidrains/vector-quantize-pytorch
- MishaLaskin vqvae: https://github.com/MishaLaskin/vqvae
"""

# =============================================================================
# CONNECTION TO MODULE 12
# =============================================================================

"""
PEDAGOGICAL CONNECTIONS:

- FROM VAE (12.2):
  VQ-VAE replaces Gaussian sampling with discrete codebook lookup.
  Compare: continuous z ~ N(mu, sigma) vs discrete z_q = nearest(z_e)
  Key insight: both are bottleneck representations, different constraints

- FROM DCGAN (12.1.2):
  VQGAN adds discriminator (PatchGAN) for sharper outputs.
  Same adversarial training principle, applied to reconstruction.

- FROM Pix2Pix (12.1.4):
  PatchGAN discriminator is identical to Pix2Pix!
  Perceptual loss uses VGG like Neural Style Transfer.

- TO Taming Transformers (12.6.1):
  VQGAN tokens become input to autoregressive transformer.
  Image = sequence of discrete tokens = can be generated like text!
  This is the foundation of DALL-E architecture.

- TO DALL-E:
  DALL-E 1 = VQ-VAE + GPT
  Text tokens + image tokens concatenated, GPT predicts next token
  VQ-VAE tokens enable treating images like language
"""

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = [
    "torch",
    "torchvision",
    "numpy",
    "PIL",
    "matplotlib",
    "tqdm",
    "lpips",  # For perceptual loss (optional, can use VGG)
]

if __name__ == "__main__":
    print("This is a placeholder file for VQ-VAE/VQGAN exercise.")
    print("Content will be generated based on the specifications above.")
    print()
    print("Key files to create:")
    print("  - simple_vqvae.py (MNIST demo)")
    print("  - vqvae_solution.py (full implementation)")
    print("  - vqvae_starter.py (student template)")
    print("  - vqgan_solution.py (with adversarial training)")
    print("  - codebook_analysis.py (visualization)")
    print("  - README.rst (replace this placeholder)")
