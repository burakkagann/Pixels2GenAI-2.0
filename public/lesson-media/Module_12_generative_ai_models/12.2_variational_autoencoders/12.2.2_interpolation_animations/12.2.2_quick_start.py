import torch
import imageio.v2 as imageio
from vae_model import VAE, LATENT_DIM

vae = VAE(latent_dim=LATENT_DIM)
vae.load_state_dict(torch.load('vae_weights.pth', map_location='cpu'))
vae.eval()

torch.manual_seed(42)
z_start = torch.randn(LATENT_DIM)
z_end   = torch.randn(LATENT_DIM)

frames = []
for i in range(30):
    t = i / 29
    z = ((1 - t) * z_start + t * z_end).unsqueeze(0)
    with torch.no_grad():
        img = vae.decoder(z)
    img = ((img[0] + 1) / 2).clamp(0, 1).permute(1, 2, 0).numpy()
    frames.append((img * 255).astype('uint8'))

imageio.mimsave('my_animation.gif', frames, fps=15)
