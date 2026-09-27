import torch
import torch.nn as nn
import torch.nn.functional as F

class SimpleCVAE(nn.Module):
    def __init__(self, latent_dim=16, num_classes=10):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_classes = num_classes

        # TODO: 784 (image) + 10 (label) = 794 input features
        self.encoder_fc1 = nn.Linear(???, 256)
        self.encoder_fc2 = nn.Linear(256, 128)
        self.fc_mu      = nn.Linear(128, latent_dim)
        self.fc_logvar  = nn.Linear(128, latent_dim)

        # TODO: latent_dim + 10 (label) input features
        self.decoder_fc1 = nn.Linear(???, 128)
        self.decoder_fc2 = nn.Linear(128, 256)
        self.decoder_fc3 = nn.Linear(256, 784)

    def encode(self, x, y):
        combined = ???                  # TODO: concat along dim=1
        h = F.relu(self.encoder_fc1(combined))
        h = F.relu(self.encoder_fc2(h))
        return self.fc_mu(h), self.fc_logvar(h)

    def reparameterize(self, mu, logvar):
        # TODO: std = exp(0.5*logvar); z = mu + std * eps
        pass

    def decode(self, z, y):
        combined = ???                  # TODO: concat along dim=1
        h = F.relu(self.decoder_fc1(combined))
        h = F.relu(self.decoder_fc2(h))
        return torch.sigmoid(self.decoder_fc3(h))

def cvae_loss(recon, x, mu, logvar):
    # TODO: BCE reconstruction + KL divergence
    pass
