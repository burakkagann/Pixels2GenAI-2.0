"""Minimal autoregressive transformer over image tokens.

Demonstrates the second-stage model in the VQ-VAE / VQ-GAN + Transformer
architecture: given sequences of token indices (output of a VQ-VAE encoder),
train a tiny GPT-style transformer to predict the next token.

For this demo, the "tokens" are simulated as random integer sequences. To use
real image tokens, swap `make_dummy_dataset()` with a function that runs your
VQ-VAE encoder over an image dataset and returns its index sequences.

Author: Pixels2GenAI Project
"""

import math
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset


VOCAB_SIZE = 64        # codebook size (must match your VQ-VAE)
SEQ_LEN = 49           # 7x7 grid of tokens, raster-ordered
EMBED_DIM = 128
NUM_HEADS = 4
NUM_LAYERS = 4
NUM_EPOCHS = 5
BATCH_SIZE = 64
LEARNING_RATE = 3e-4


class CausalSelfAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.attn = nn.MultiheadAttention(EMBED_DIM, NUM_HEADS, batch_first=True)
        # Lower-triangular mask blocks future positions.
        mask = torch.triu(torch.ones(SEQ_LEN, SEQ_LEN), diagonal=1).bool()
        self.register_buffer("causal_mask", mask)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq = x.size(1)
        out, _ = self.attn(x, x, x, attn_mask=self.causal_mask[:seq, :seq], need_weights=False)
        return out


class TransformerBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.norm1 = nn.LayerNorm(EMBED_DIM)
        self.attn = CausalSelfAttention()
        self.norm2 = nn.LayerNorm(EMBED_DIM)
        self.mlp = nn.Sequential(
            nn.Linear(EMBED_DIM, 4 * EMBED_DIM),
            nn.GELU(),
            nn.Linear(4 * EMBED_DIM, EMBED_DIM),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.norm1(x))
        x = x + self.mlp(self.norm2(x))
        return x


class ImageGPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok_emb = nn.Embedding(VOCAB_SIZE, EMBED_DIM)
        self.pos_emb = nn.Embedding(SEQ_LEN, EMBED_DIM)
        self.blocks = nn.ModuleList([TransformerBlock() for _ in range(NUM_LAYERS)])
        self.norm = nn.LayerNorm(EMBED_DIM)
        self.head = nn.Linear(EMBED_DIM, VOCAB_SIZE)
        self.register_buffer("positions", torch.arange(SEQ_LEN))

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        b, s = tokens.shape
        x = self.tok_emb(tokens) + self.pos_emb(self.positions[:s])
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        return self.head(x)        # (B, S, vocab_size) — logits over next token at each position

    @torch.no_grad()
    def generate(self, num_samples: int = 4, temperature: float = 1.0) -> torch.Tensor:
        """Autoregressive sampling: predict one token at a time, left to right."""
        device = next(self.parameters()).device
        tokens = torch.zeros(num_samples, 1, dtype=torch.long, device=device)
        for i in range(SEQ_LEN - 1):
            logits = self.forward(tokens)[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            tokens = torch.cat([tokens, next_token], dim=1)
        return tokens


def make_dummy_dataset(num_samples: int = 1000) -> TensorDataset:
    """Fake training data: random integer sequences. Real use case feeds VQ-VAE token sequences."""
    sequences = torch.randint(0, VOCAB_SIZE, (num_samples, SEQ_LEN))
    return TensorDataset(sequences)


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    dataset = make_dummy_dataset()
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model = ImageGPT().to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(NUM_EPOCHS):
        running = 0.0
        for (tokens,) in loader:
            tokens = tokens.to(device)
            # Standard autoregressive setup: predict tokens[i+1] from tokens[:i+1]
            input_tokens = tokens[:, :-1]
            target_tokens = tokens[:, 1:]

            logits = model(input_tokens)
            loss = criterion(logits.reshape(-1, VOCAB_SIZE), target_tokens.reshape(-1))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running += loss.item()

        print(f"Epoch {epoch + 1}/{NUM_EPOCHS}  loss={running / len(loader):.4f}")

    print("\nSampling 4 sequences autoregressively:")
    samples = model.generate(num_samples=4)
    print(samples)
    print(f"\nShape: {samples.shape}  — would decode to {SEQ_LEN}-token image grids via VQ-VAE.")


if __name__ == "__main__":
    main()
