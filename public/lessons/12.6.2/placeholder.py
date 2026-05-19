# =============================================================================
# IMPLEMENTATION SPECIFICATIONS
# =============================================================================

"""
KEY COMPONENTS TO IMPLEMENT:

1. Patchify and Unpatchify Operations
   def patchify(x, patch_size=2):
       '''Convert spatial tensor to sequence of patches.

       Args:
           x: (B, C, H, W) input tensor
           patch_size: size of each patch

       Returns:
           patches: (B, num_patches, patch_dim)
       '''
       B, C, H, W = x.shape
       assert H % patch_size == 0 and W % patch_size == 0

       # Reshape: (B, C, H//p, p, W//p, p) -> (B, H//p * W//p, p*p*C)
       x = x.reshape(B, C, H // patch_size, patch_size, W // patch_size, patch_size)
       x = x.permute(0, 2, 4, 3, 5, 1)  # (B, H//p, W//p, p, p, C)
       x = x.reshape(B, -1, patch_size * patch_size * C)
       return x

   def unpatchify(x, patch_size=2, H=32, W=32, C=4):
       '''Convert patch sequence back to spatial tensor.'''
       B, N, _ = x.shape
       x = x.reshape(B, H // patch_size, W // patch_size, patch_size, patch_size, C)
       x = x.permute(0, 5, 1, 3, 2, 4)  # (B, C, H//p, p, W//p, p)
       x = x.reshape(B, C, H, W)
       return x

2. Adaptive Layer Normalization (AdaLN)
   class AdaLN(nn.Module):
       '''Adaptive Layer Normalization - key DiT innovation.'''

       def __init__(self, hidden_size, num_classes=1000, timestep_dim=256):
           super().__init__()
           self.norm = nn.LayerNorm(hidden_size, elementwise_affine=False)

           # MLP to predict scale (γ) and shift (β) from timestep + class
           self.adaLN_modulation = nn.Sequential(
               nn.SiLU(),
               nn.Linear(timestep_dim, 6 * hidden_size),  # 6 for 2 norms in block
           )

       def forward(self, x, c):
           '''
           Args:
               x: (B, N, D) input tokens
               c: (B, D) conditioning vector (timestep + class embedding)

           Returns:
               Normalized and modulated x
           '''
           # Predict modulation parameters
           shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = \
               self.adaLN_modulation(c).chunk(6, dim=-1)

           # Apply adaptive normalization
           x_norm = self.norm(x)
           x_modulated = x_norm * (1 + scale_msa.unsqueeze(1)) + shift_msa.unsqueeze(1)

           return x_modulated, (gate_msa, shift_mlp, scale_mlp, gate_mlp)

3. DiT Block
   class DiTBlock(nn.Module):
       '''Single DiT transformer block with AdaLN conditioning.'''

       def __init__(self, hidden_size, num_heads, mlp_ratio=4.0):
           super().__init__()
           self.norm1 = nn.LayerNorm(hidden_size, elementwise_affine=False)
           self.attn = nn.MultiheadAttention(hidden_size, num_heads, batch_first=True)
           self.norm2 = nn.LayerNorm(hidden_size, elementwise_affine=False)

           mlp_hidden = int(hidden_size * mlp_ratio)
           self.mlp = nn.Sequential(
               nn.Linear(hidden_size, mlp_hidden),
               nn.GELU(),
               nn.Linear(mlp_hidden, hidden_size),
           )

           # AdaLN modulation
           self.adaLN_modulation = nn.Sequential(
               nn.SiLU(),
               nn.Linear(hidden_size, 6 * hidden_size),
           )

       def forward(self, x, c):
           # Get modulation parameters
           shift_msa, scale_msa, gate_msa, shift_mlp, scale_mlp, gate_mlp = \
               self.adaLN_modulation(c).chunk(6, dim=-1)

           # Attention block with AdaLN
           x_norm = self.norm1(x) * (1 + scale_msa.unsqueeze(1)) + shift_msa.unsqueeze(1)
           attn_out, _ = self.attn(x_norm, x_norm, x_norm)
           x = x + gate_msa.unsqueeze(1) * attn_out

           # MLP block with AdaLN
           x_norm = self.norm2(x) * (1 + scale_mlp.unsqueeze(1)) + shift_mlp.unsqueeze(1)
           x = x + gate_mlp.unsqueeze(1) * self.mlp(x_norm)

           return x

4. Full DiT Model
   class DiT(nn.Module):
       '''Diffusion Transformer for image generation.'''

       def __init__(
           self,
           input_size=32,       # Latent size
           patch_size=2,
           in_channels=4,       # Latent channels
           hidden_size=1152,    # DiT-XL
           depth=28,            # Number of transformer blocks
           num_heads=16,
           mlp_ratio=4.0,
           num_classes=1000,
           learn_sigma=True,
       ):
           super().__init__()
           self.patch_size = patch_size
           self.num_patches = (input_size // patch_size) ** 2

           # Patch embedding
           self.x_embedder = nn.Linear(patch_size * patch_size * in_channels, hidden_size)

           # Positional embedding
           self.pos_embed = nn.Parameter(torch.zeros(1, self.num_patches, hidden_size))

           # Timestep embedding (sinusoidal like DDPM)
           self.t_embedder = TimestepEmbedding(hidden_size)

           # Class embedding
           self.y_embedder = nn.Embedding(num_classes, hidden_size)

           # Transformer blocks
           self.blocks = nn.ModuleList([
               DiTBlock(hidden_size, num_heads, mlp_ratio)
               for _ in range(depth)
           ])

           # Final layer
           self.final_layer = FinalLayer(hidden_size, patch_size, in_channels * (2 if learn_sigma else 1))

       def forward(self, x, t, y):
           '''
           Args:
               x: (B, C, H, W) noisy latent
               t: (B,) timesteps
               y: (B,) class labels

           Returns:
               noise prediction (B, C, H, W)
           '''
           # Patchify
           x = patchify(x, self.patch_size)
           x = self.x_embedder(x) + self.pos_embed

           # Conditioning
           t_emb = self.t_embedder(t)
           y_emb = self.y_embedder(y)
           c = t_emb + y_emb  # Combine timestep and class

           # Transformer blocks
           for block in self.blocks:
               x = block(x, c)

           # Final layer and unpatchify
           x = self.final_layer(x, c)
           x = unpatchify(x, self.patch_size)

           return x

5. Training Loop (Same as DDPM, different backbone)
   def train_dit(model, dataloader, optimizer, device, epochs=100):
       model.train()

       for epoch in range(epochs):
           for images, labels in dataloader:
               images, labels = images.to(device), labels.to(device)

               # Sample random timesteps
               t = torch.randint(0, 1000, (images.size(0),), device=device)

               # Add noise (same as DDPM)
               noise = torch.randn_like(images)
               x_t = q_sample(images, t, noise)

               # Predict noise with DiT
               noise_pred = model(x_t, t, labels)

               # MSE loss (same as DDPM!)
               loss = F.mse_loss(noise_pred, noise)

               optimizer.zero_grad()
               loss.backward()
               optimizer.step()

SUGGESTED FILE STRUCTURE:
- dit_architecture.py: Full DiT model implementation
- adaln.py: Adaptive Layer Normalization module
- dit_blocks.py: DiT block components
- train_dit.py: Training script
- generate_with_dit.py: Sampling and generation
- compare_to_unet.py: DiT vs U-Net comparison
- README.rst (replace this placeholder)
"""

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

DIT_CONFIGS = {
    "DiT-S/2": {
        "hidden_size": 384,
        "depth": 12,
        "num_heads": 6,
        "patch_size": 2,
        "params": "33M",
        "flops": "1.4G",
    },
    "DiT-S/4": {
        "hidden_size": 384,
        "depth": 12,
        "num_heads": 6,
        "patch_size": 4,
        "params": "33M",
        "flops": "0.4G",
    },
    "DiT-B/2": {
        "hidden_size": 768,
        "depth": 12,
        "num_heads": 12,
        "patch_size": 2,
        "params": "130M",
        "flops": "5.6G",
    },
    "DiT-L/2": {
        "hidden_size": 1024,
        "depth": 24,
        "num_heads": 16,
        "patch_size": 2,
        "params": "458M",
        "flops": "19.7G",
    },
    "DiT-XL/2": {
        "hidden_size": 1152,
        "depth": 28,
        "num_heads": 16,
        "patch_size": 2,
        "params": "675M",
        "flops": "29.1G",
        "fid_256": 2.27,  # State-of-the-art!
    },
}

# =============================================================================
# SCALING LAW DATA (From DiT Paper)
# =============================================================================

SCALING_DATA = {
    # FID-50K on ImageNet 256x256 (lower is better)
    "DiT-S/8": {"params": "33M", "fid": 68.4},
    "DiT-S/4": {"params": "33M", "fid": 43.5},
    "DiT-S/2": {"params": "33M", "fid": 27.3},
    "DiT-B/4": {"params": "130M", "fid": 43.0},
    "DiT-B/2": {"params": "130M", "fid": 12.6},
    "DiT-L/4": {"params": "458M", "fid": 26.7},
    "DiT-L/2": {"params": "458M", "fid": 5.02},
    "DiT-XL/2": {"params": "675M", "fid": 2.27},  # SOTA
}

# =============================================================================
# EXPECTED OUTPUTS
# =============================================================================

"""
OUTPUT FILES TO GENERATE:

1. dit_architecture.png
   - Visual diagram comparing DiT to U-Net
   - Show patchify → transformer blocks → unpatchify

2. patch_visualization.png
   - Image divided into patches
   - Patches as token sequence
   - Position embeddings visualized

3. adaln_comparison.png
   - Standard LayerNorm vs AdaLN
   - Show how conditioning affects normalization

4. dit_generated_samples.png
   - Grid of class-conditional generations
   - Different ImageNet classes

5. scaling_plot.png
   - X: Model parameters (log scale)
   - Y: FID score
   - Show clear scaling trend

6. dit_vs_unet.png
   - Same noise, same timestep
   - DiT prediction vs U-Net prediction

7. model_size_comparison.png
   - DiT-S vs DiT-B vs DiT-L vs DiT-XL outputs
   - Show quality improvement with size

8. attention_visualization.png
   - Attention maps from DiT blocks
   - Show what the model attends to
"""

# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

TRAINING_CONFIG = {
    # For DiT-S/2 (trainable on RTX 5070Ti)
    "model_size": "DiT-S/2",
    "input_size": 32,           # Latent size (256 image / 8 VAE)
    "patch_size": 2,
    "in_channels": 4,           # VAE latent channels
    "hidden_size": 384,
    "depth": 12,
    "num_heads": 6,
    "learning_rate": 1e-4,
    "batch_size": 64,           # Effective (may need gradient accumulation)
    "epochs": 100,
    "warmup_steps": 5000,
    "ema_decay": 0.9999,
    "mixed_precision": "bf16",
}

INFERENCE_CONFIG = {
    "num_sampling_steps": 250,
    "cfg_scale": 4.0,           # Classifier-free guidance
    "sampler": "ddpm",          # or "ddim" for faster
}

# =============================================================================
# RESOURCES
# =============================================================================

"""
PAPERS:
- DiT: https://arxiv.org/abs/2212.09748
- DiffiT: https://arxiv.org/abs/2312.02139
- SiT: https://arxiv.org/abs/2401.08740
- U-ViT: https://arxiv.org/abs/2209.12152
- Pixart-Alpha: https://arxiv.org/abs/2310.00426
- ViT: https://arxiv.org/abs/2010.11929 (Vision Transformer)

TUTORIALS:
- DiT Project Page: https://www.wpeebles.com/DiT
- Hugging Face DiT: https://huggingface.co/docs/diffusers/api/pipelines/dit
- labml.ai DiT: https://nn.labml.ai/diffusion/dit/index.html

GITHUB:
- Official DiT: https://github.com/facebookresearch/DiT
- NVIDIA DiffiT: https://github.com/NVlabs/DiffiT
- Hugging Face Diffusers: https://github.com/huggingface/diffusers
- Pixart-Alpha: https://github.com/PixArt-alpha/PixArt-alpha

PRETRAINED MODELS:
- DiT-XL/2 ImageNet: https://huggingface.co/facebook/DiT-XL-2-256
- Pixart Models: https://huggingface.co/PixArt-alpha

INDUSTRY:
- OpenAI SORA: https://openai.com/sora (DiT for video)
- Stable Diffusion 3: https://stability.ai/stable-diffusion-3
"""

# =============================================================================
# CONNECTION TO MODULE 12
# =============================================================================

"""
PEDAGOGICAL CONNECTIONS:

- FROM DDPM (12.4.1):
  SAME DIFFUSION PROCESS, DIFFERENT BACKBONE!
  DiT predicts noise just like DDPM U-Net.
  Training objective is identical: MSE on noise.
  Only the architecture is different.

- FROM ControlNet (12.4.2):
  ControlNet concepts extend to DiT.
  Can add control mechanisms to transformer architecture.
  Active research area.

- FROM Taming Transformers (12.6.1):
  Both use transformers for images.
  Taming: autoregressive token prediction
  DiT: diffusion noise prediction
  Different generation paradigms, same backbone idea.

- FROM Pix2Pix (12.1.4):
  U-Net in Pix2Pix uses skip connections for spatial info.
  DiT uses global attention - every patch sees every patch.
  More flexible, but more compute.

- FROM VQ-VAE (12.3.2):
  DiT often works in latent space (like Latent Diffusion).
  VAE encoder → latent → DiT denoises → VAE decoder.
  Efficiency of latent space + power of transformer.

- TO Flow Matching (12.7.1):
  Flow matching can use DiT backbone too!
  Architecture orthogonal to generation paradigm.
  Best practices transfer across approaches.

- INDUSTRY RELEVANCE:
  DiT is THE architecture for modern generative AI.
  SORA, SD3, and future models all use DiT variants.
  Understanding DiT = understanding state-of-the-art.
"""

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = [
    "torch",
    "torchvision",
    "diffusers>=0.21.0",
    "transformers",
    "accelerate",
    "einops",            # For tensor operations
    "timm",              # PyTorch image models (optional)
    "numpy",
    "PIL",
    "matplotlib",
    "tqdm",
]

if __name__ == "__main__":
    print("This is a placeholder file for DiT exercise.")
    print("Content will be generated based on the specifications above.")
    print()
    print("Key files to create:")
    print("  - dit_architecture.py (full DiT model)")
    print("  - adaln.py (adaptive layer norm)")
    print("  - train_dit.py (training script)")
    print("  - generate_with_dit.py (sampling)")
    print("  - compare_to_unet.py (DiT vs U-Net)")
    print("  - README.rst (replace this placeholder)")
