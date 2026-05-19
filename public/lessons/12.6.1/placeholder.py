# =============================================================================
# IMPLEMENTATION SPECIFICATIONS
# =============================================================================

"""
KEY COMPONENTS TO IMPLEMENT:

1. Load Pretrained VQGAN Tokenizer
   from taming.models.vqgan import VQModel
   import yaml

   # Load config
   with open("vqgan_imagenet_f16_8192.yaml", "r") as f:
       config = yaml.safe_load(f)

   # Load model
   vqgan = VQModel(**config["model"]["params"])
   vqgan.load_state_dict(torch.load("vqgan_imagenet_f16_8192.ckpt"))
   vqgan.eval()

   # Tokenize image
   def encode_image(image, vqgan):
       with torch.no_grad():
           z = vqgan.encode(image)
           _, _, indices = vqgan.quantize(z)
           return indices  # Shape: (batch, 16, 16)

   # Decode tokens back to image
   def decode_tokens(indices, vqgan):
       with torch.no_grad():
           z_q = vqgan.quantize.get_codebook_entry(indices)
           image = vqgan.decode(z_q)
           return image

2. Autoregressive Transformer Architecture
   import torch
   import torch.nn as nn

   class ImageGPT(nn.Module):
       def __init__(self, vocab_size=8192, n_positions=256, n_embd=1024,
                    n_layer=24, n_head=16, n_classes=None):
           super().__init__()
           self.tok_emb = nn.Embedding(vocab_size, n_embd)
           self.pos_emb = nn.Embedding(n_positions, n_embd)

           if n_classes:  # Class conditioning
               self.class_emb = nn.Embedding(n_classes, n_embd)

           decoder_layer = nn.TransformerDecoderLayer(
               d_model=n_embd, nhead=n_head, batch_first=True
           )
           self.transformer = nn.TransformerDecoder(decoder_layer, n_layer)
           self.ln_f = nn.LayerNorm(n_embd)
           self.head = nn.Linear(n_embd, vocab_size)

       def forward(self, tokens, class_label=None):
           # tokens: (batch, seq_len)
           batch, seq_len = tokens.shape
           positions = torch.arange(seq_len, device=tokens.device)

           # Embeddings
           x = self.tok_emb(tokens) + self.pos_emb(positions)

           # Add class conditioning
           if class_label is not None and hasattr(self, 'class_emb'):
               class_embed = self.class_emb(class_label).unsqueeze(1)
               x = torch.cat([class_embed, x], dim=1)

           # Causal mask
           mask = nn.Transformer.generate_square_subsequent_mask(x.size(1))

           # Transformer
           x = self.transformer(x, x, tgt_mask=mask)
           x = self.ln_f(x)
           logits = self.head(x)

           return logits

3. Training Loop
   def train_step(model, vqgan, images, optimizer, criterion):
       # Tokenize images
       with torch.no_grad():
           tokens = encode_image(images, vqgan)  # (B, 16, 16)
           tokens = tokens.view(tokens.size(0), -1)  # (B, 256)

       # Shift for teacher forcing
       input_tokens = tokens[:, :-1]
       target_tokens = tokens[:, 1:]

       # Forward pass
       logits = model(input_tokens)
       loss = criterion(logits.view(-1, 8192), target_tokens.view(-1))

       # Backward pass
       optimizer.zero_grad()
       loss.backward()
       optimizer.step()

       return loss.item()

4. Autoregressive Sampling
   @torch.no_grad()
   def generate(model, vqgan, n_tokens=256, temperature=1.0,
                top_k=100, class_label=None):
       model.eval()

       # Start with empty or class token
       if class_label is not None:
           tokens = torch.tensor([[class_label]])  # Will be class embedding
       else:
           tokens = torch.zeros(1, 0, dtype=torch.long)

       for i in range(n_tokens):
           # Get logits for next token
           logits = model(tokens)[:, -1, :]  # (1, vocab_size)
           logits = logits / temperature

           # Top-k sampling
           if top_k > 0:
               v, _ = torch.topk(logits, top_k)
               logits[logits < v[:, -1:]] = -float('inf')

           # Sample
           probs = F.softmax(logits, dim=-1)
           next_token = torch.multinomial(probs, num_samples=1)

           # Append
           tokens = torch.cat([tokens, next_token], dim=1)

       # Reshape to image grid and decode
       token_grid = tokens[:, -256:].view(1, 16, 16)
       image = decode_tokens(token_grid, vqgan)

       return image, tokens

5. Animation of Generation Process
   def generate_with_frames(model, vqgan, n_tokens=256, save_every=16):
       frames = []
       tokens = torch.zeros(1, 0, dtype=torch.long)

       for i in range(n_tokens):
           # Generate next token
           logits = model(tokens)[:, -1, :]
           next_token = torch.multinomial(F.softmax(logits, dim=-1), 1)
           tokens = torch.cat([tokens, next_token], dim=1)

           # Save frame periodically
           if (i + 1) % save_every == 0:
               # Partial decode (pad with zeros for missing tokens)
               partial = F.pad(tokens, (0, 256 - tokens.size(1)))
               partial_grid = partial.view(1, 16, 16)
               frame = decode_tokens(partial_grid, vqgan)
               frames.append(frame)

       return frames

SUGGESTED FILE STRUCTURE:
- tokenize_images.py: VQGAN tokenization utilities
- image_gpt.py: Transformer architecture
- train_transformer.py: Training script
- generate_images.py: Sampling and generation
- generation_animation.py: Create token-by-token animation
- class_conditional.py: Class-conditioned generation
- README.rst (replace this placeholder)
"""

# =============================================================================
# ARCHITECTURE DETAILS
# =============================================================================

TRANSFORMER_ARCHITECTURES = {
    "small": {
        "n_layer": 12,
        "n_head": 8,
        "n_embd": 512,
        "params": "~85M",
        "training_time": "4-6 hours",
    },
    "medium": {
        "n_layer": 24,
        "n_head": 16,
        "n_embd": 1024,
        "params": "~350M",
        "training_time": "8-12 hours",
    },
    "large": {
        "n_layer": 36,
        "n_head": 20,
        "n_embd": 1280,
        "params": "~760M",
        "training_time": "16+ hours",
    },
}

# =============================================================================
# EXPECTED OUTPUTS
# =============================================================================

"""
OUTPUT FILES TO GENERATE:

1. token_visualization.png
   - Original image + token grid visualization
   - Show codebook indices as colored pixels

2. generation_sequence.gif
   - Animation showing tokens appearing one by one
   - Image gradually becoming coherent

3. class_conditional_grid.png
   - 3x3 or 4x4 grid of different classes
   - Same model, different class tokens

4. completion_demo.png
   - Left half given, right half generated
   - Shows model understands image structure

5. temperature_comparison.png
   - Same prompt, temperatures: 0.5, 0.7, 1.0, 1.2
   - Show diversity/quality tradeoff

6. sampling_methods.png
   - Top-k vs Top-p vs Temperature comparison
   - Different sampling strategies

7. fabric_autoregressive.png
   - African fabric generated autoregressively
   - Compare to DCGAN result
"""

# =============================================================================
# TRAINING CONFIGURATION
# =============================================================================

VQGAN_CONFIG = {
    "pretrained_model": "vqgan_imagenet_f16_8192",
    "codebook_size": 8192,
    "latent_dim": 256,
    "downsample_factor": 16,
    # 256x256 image → 16x16 tokens = 256 tokens
}

TRANSFORMER_CONFIG = {
    "vocab_size": 8192,        # Same as VQGAN codebook
    "n_positions": 256,        # 16x16 tokens
    "n_embd": 1024,            # Hidden dimension
    "n_layer": 24,             # Transformer layers
    "n_head": 16,              # Attention heads
    "dropout": 0.1,
    "learning_rate": 4e-4,
    "batch_size": 16,
    "warmup_steps": 4000,
    "total_steps": 100000,
    "gradient_clip": 1.0,
}

SAMPLING_CONFIG = {
    "temperature": 1.0,        # 0.7-1.0 typical
    "top_k": 100,              # 0 = disabled
    "top_p": 0.95,             # Nucleus sampling
    "num_tokens": 256,         # Full image
}

# =============================================================================
# RESOURCES
# =============================================================================

"""
PAPERS:
- Taming Transformers: https://arxiv.org/abs/2012.09841
- DALL-E 1: https://arxiv.org/abs/2102.12092
- ImageGPT: https://openai.com/research/image-gpt
- Parti: https://arxiv.org/abs/2206.10789
- ViT-VQGAN: https://arxiv.org/abs/2110.04627

TUTORIALS:
- CompVis Project Page: https://compvis.github.io/taming-transformers/
- Hugging Face Transformers: https://huggingface.co/docs/transformers
- Jay Alammar Visual Transformer: https://jalammar.github.io/illustrated-transformer/

GITHUB:
- Official Taming Transformers: https://github.com/CompVis/taming-transformers
- VQGAN-CLIP: https://github.com/nerdyrodent/VQGAN-CLIP
- lucidrains x-transformers: https://github.com/lucidrains/x-transformers
- minGPT: https://github.com/karpathy/minGPT

PRETRAINED MODELS:
- VQGAN ImageNet: https://heibox.uni-heidelberg.de/d/a7530b09fed84f80a887/
- Taming Transformers Checkpoints: https://github.com/CompVis/taming-transformers#overview-of-pretrained-models
"""

# =============================================================================
# CONNECTION TO MODULE 12
# =============================================================================

"""
PEDAGOGICAL CONNECTIONS:

- FROM VQ-VAE/VQGAN (12.3.2):
  DIRECTLY USES VQGAN as tokenizer!
  This is why we learned VQ-VAE: to enable transformer generation.
  VQ-VAE tokens become the "words" that transformer predicts.

- FROM GANs (12.1):
  VQGAN uses adversarial training for sharp tokens.
  Discriminator in VQGAN ensures high-quality discrete representations.
  GAN + Transformer = powerful combination.

- FROM DCGAN (12.1.2):
  Different generation paradigm!
  DCGAN: noise → all pixels at once
  Taming Transformers: start → token → token → ... → image
  Compare outputs on same dataset.

- FROM DDPM (12.4.1):
  Completely different approach to generation.
  DDPM: iterative denoising of all pixels
  Autoregressive: sequential token prediction
  Both work! Different tradeoffs.

- TO DiT (12.6.2):
  "What if we used transformers WITH diffusion?"
  DiT keeps diffusion process, replaces U-Net with transformer.
  Best of both worlds: transformer scalability + diffusion quality.

- HISTORICAL CONTEXT:
  Taming Transformers → DALL-E 1 (2021)
  Then diffusion models took over (2022+)
  Now DiT combines both approaches (2023+)
"""

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = [
    "torch",
    "torchvision",
    "transformers",      # HuggingFace transformers
    "einops",            # Tensor operations
    "omegaconf",         # Config loading
    "taming-transformers",  # Official repo (or manual implementation)
    "numpy",
    "PIL",
    "matplotlib",
    "imageio",           # For GIF generation
    "tqdm",
]

if __name__ == "__main__":
    print("This is a placeholder file for Taming Transformers exercise.")
    print("Content will be generated based on the specifications above.")
    print()
    print("Key files to create:")
    print("  - tokenize_images.py (VQGAN tokenization)")
    print("  - image_gpt.py (transformer architecture)")
    print("  - train_transformer.py (training script)")
    print("  - generate_images.py (sampling)")
    print("  - generation_animation.py (token-by-token viz)")
    print("  - README.rst (replace this placeholder)")
