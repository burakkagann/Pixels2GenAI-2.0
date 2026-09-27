import torch
import torch.nn as nn
import torch.nn.functional as F

class VectorQuantizer(nn.Module):
    def __init__(self, codebook_size: int, embedding_dim: int, commitment_cost: float):
        super().__init__()
        # TODO: create codebook as nn.Embedding(codebook_size, embedding_dim)
        # TODO: initialise its weights uniformly in [-1/K, 1/K]
        # TODO: store commitment_cost as self attribute
        pass

    def forward(self, z_e):
        b, c, h, w = z_e.shape
        z_e_flat = z_e.permute(0, 2, 3, 1).reshape(-1, c)

        # TODO: compute pairwise squared distances between z_e_flat and codebook
        # (use the (a-b)^2 = a^2 - 2ab + b^2 expansion)

        # TODO: indices = argmin over codebook dim
        # TODO: z_q_flat = self.codebook(indices)

        # TODO: codebook_loss = MSE(z_q_flat, z_e_flat.detach())
        # TODO: commitment_loss = MSE(z_q_flat.detach(), z_e_flat)
        # TODO: loss = codebook_loss + self.commitment_cost * commitment_loss

        # TODO: apply straight-through estimator
        # z_q_flat = z_e_flat + (z_q_flat - z_e_flat).detach()

        # TODO: reshape z_q_flat back to (b, c, h, w) shape

        # TODO: return z_q, loss, indices.reshape(b, h, w)
        pass
