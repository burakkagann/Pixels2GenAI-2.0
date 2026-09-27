"""Minimal VQ-VAE demo: encoder, vector-quantised bottleneck, decoder.

Trains briefly on MNIST to demonstrate the discrete codebook learning. Not a
production-quality implementation - the codebook size, embedding dim, and training
schedule are sized for a 60-second run on a laptop.

Author: Pixels2GenAI Project
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


# Configuration sized for fast iteration; bump for real quality.
CODEBOOK_SIZE = 64           # number of discrete tokens
EMBEDDING_DIM = 32           # dimension of each codebook vector
COMMITMENT_COST = 0.25       # weight on the commitment-loss term (paper default)
NUM_EPOCHS = 3               # bump to 10+ for cleaner reconstructions
BATCH_SIZE = 256
LEARNING_RATE = 1e-3


class VectorQuantizer(nn.Module):
    """Maps continuous encoder outputs to nearest discrete codebook entries.

    Implements the straight-through estimator: forward pass uses the quantised
    vector; backward pass copies gradients straight to the encoder, as if
    quantisation were the identity.
    """

    def __init__(self, codebook_size: int, embedding_dim: int, commitment_cost: float):
        super().__init__()
        self.codebook = nn.Embedding(codebook_size, embedding_dim)
        nn.init.uniform_(self.codebook.weight, -1.0 / codebook_size, 1.0 / codebook_size)
        self.commitment_cost = commitment_cost

    def forward(self, z_e: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # z_e: (B, C, H, W). Flatten spatial -> (B*H*W, C).
        b, c, h, w = z_e.shape
        z_e_flat = z_e.permute(0, 2, 3, 1).reshape(-1, c)

        # Nearest neighbour by squared L2 distance.
        d = (z_e_flat.pow(2).sum(1, keepdim=True)
             - 2 * z_e_flat @ self.codebook.weight.t()
             + self.codebook.weight.pow(2).sum(1))
        indices = d.argmin(dim=1)
        z_q_flat = self.codebook(indices)

        # Losses: codebook loss pulls codes toward encoder; commitment loss pulls
        # encoder toward codes. .detach() on each side controls gradient flow.
        codebook_loss = F.mse_loss(z_q_flat, z_e_flat.detach())
        commitment_loss = F.mse_loss(z_q_flat.detach(), z_e_flat)
        loss = codebook_loss + self.commitment_cost * commitment_loss

        # Straight-through: quantised forward, identity backward.
        z_q_flat = z_e_flat + (z_q_flat - z_e_flat).detach()
        z_q = z_q_flat.reshape(b, h, w, c).permute(0, 3, 1, 2)

        return z_q, loss, indices.reshape(b, h, w)


class VQVAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 32, 4, 2, 1), nn.ReLU(),    # 28 -> 14
            nn.Conv2d(32, EMBEDDING_DIM, 4, 2, 1),    # 14 -> 7
        )
        self.quantizer = VectorQuantizer(CODEBOOK_SIZE, EMBEDDING_DIM, COMMITMENT_COST)
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(EMBEDDING_DIM, 32, 4, 2, 1), nn.ReLU(),  # 7 -> 14
            nn.ConvTranspose2d(32, 1, 4, 2, 1), nn.Sigmoid(),            # 14 -> 28
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        z_e = self.encoder(x)
        z_q, vq_loss, indices = self.quantizer(z_e)
        x_hat = self.decoder(z_q)
        return x_hat, vq_loss, indices


def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    transform = transforms.Compose([transforms.ToTensor()])
    train_loader = DataLoader(
        datasets.MNIST("./data", train=True, download=True, transform=transform),
        batch_size=BATCH_SIZE, shuffle=True,
    )

    model = VQVAE().to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(NUM_EPOCHS):
        running = {"recon": 0.0, "vq": 0.0}
        for images, _ in train_loader:
            images = images.to(device)
            recon, vq_loss, _ = model(images)
            recon_loss = F.mse_loss(recon, images)
            loss = recon_loss + vq_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running["recon"] += recon_loss.item()
            running["vq"] += vq_loss.item()

        n = len(train_loader)
        print(f"Epoch {epoch + 1}/{NUM_EPOCHS}  "
              f"recon={running['recon']/n:.4f}  vq={running['vq']/n:.4f}")

    # Inspect codebook usage: how many distinct tokens are actually in use?
    model.eval()
    with torch.no_grad():
        images, _ = next(iter(train_loader))
        _, _, indices = model(images.to(device))
    unique = indices.unique().numel()
    print(f"\nAfter training: {unique} of {CODEBOOK_SIZE} codebook entries used in this batch.")


if __name__ == "__main__":
    main()
