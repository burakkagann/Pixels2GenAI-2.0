import torch
import torch.nn as nn

class CVAE(nn.Module):
    def __init__(self, latent_dim=16, num_classes=10):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_classes = num_classes

        # Encoder: image (784) + label (10) -> latent distribution params
        self.encoder = nn.Sequential(
            nn.Linear(784 + num_classes, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
        )
        self.fc_mu     = nn.Linear(256, latent_dim)
        self.fc_logvar = nn.Linear(256, latent_dim)

        # Decoder: latent (16) + label (10) -> image (784)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim + num_classes, 256), nn.ReLU(),
            nn.Linear(256, 256), nn.ReLU(),
            nn.Linear(256, 784), nn.Sigmoid(),
        )

    def encode(self, x, y):  return (lambda h: (self.fc_mu(h), self.fc_logvar(h)))(self.encoder(torch.cat([x, y], dim=1)))
    def decode(self, z, y):  return self.decoder(torch.cat([z, y], dim=1))

    def generate(self, labels, n_each=1):
        with torch.no_grad():
            n = len(labels) * n_each
            y = torch.zeros(n, self.num_classes)
            for i, lbl in enumerate(labels):
                y[i*n_each:(i+1)*n_each, lbl] = 1
            z = torch.randn(n, self.latent_dim)
            return self.decode(z, y)

m = CVAE()
print(f"Generated a '7': shape {m.generate([7]).shape}")
