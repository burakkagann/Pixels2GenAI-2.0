import math
import torch
import torch.nn as nn
import torch.nn.functional as F

class CausalSelfAttention(nn.Module):
    def __init__(self, embed_dim=128, num_heads=4, seq_len=49):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        # TODO: q, k, v projections (each Linear(embed_dim, embed_dim))
        # TODO: output projection Linear(embed_dim, embed_dim)

        # TODO: causal mask buffer (lower-triangular, True where blocked)

    def forward(self, x):
        b, s, d = x.shape
        # TODO: project x to q, k, v
        # TODO: reshape each to (b, num_heads, s, head_dim)
        # TODO: compute attention scores: (q @ k.transpose(-2, -1)) / sqrt(head_dim)
        # TODO: apply causal mask: scores.masked_fill_(mask[:s, :s], float('-inf'))
        # TODO: softmax over last dim
        # TODO: out = attn @ v, reshape to (b, s, d)
        # TODO: apply output projection
        pass
