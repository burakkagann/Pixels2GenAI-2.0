import torch
import torch.nn as nn

class VAE(nn.Module):
    def __init__(self, input_dim=256, hidden_dim=128, latent_dim=8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
        )
        self.fc_mu     = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, input_dim), nn.Sigmoid(),
        )

    def forward(self, x):
        h = self.encoder(x)
        mu, logvar = self.fc_mu(h), self.fc_logvar(h)
        std = torch.exp(0.5 * logvar)
        z = mu + std * torch.randn_like(std)   # reparameterisation
        return self.decoder(z), mu, logvar

vae = VAE()
x = torch.randn(4, 256)
recon, mu, logvar = vae(x)
print(f"Input  {tuple(x.shape)} -> Latent mu {tuple(mu.shape)} -> Recon {tuple(recon.shape)}")
