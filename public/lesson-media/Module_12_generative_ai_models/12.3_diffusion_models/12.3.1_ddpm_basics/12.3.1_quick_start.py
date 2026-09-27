from denoising_diffusion_pytorch import Unet, GaussianDiffusion
from torchvision.utils import save_image
import torch

model = Unet(dim=64, dim_mults=(1, 2, 4, 8), channels=3)
diffusion = GaussianDiffusion(
    model, image_size=64, timesteps=1000, sampling_timesteps=250,
)

ckpt = torch.load('models/ddpm_african_fabrics.pt', map_location='cpu')
ema = {k.replace('ema_model.', ''): v
       for k, v in ckpt['ema'].items() if k.startswith('ema_model.')}
diffusion.load_state_dict(ema)
diffusion.eval()

with torch.no_grad():
    samples = diffusion.sample(batch_size=4)        # [4, 3, 64, 64]
samples_up = torch.nn.functional.interpolate(samples, scale_factor=4, mode='nearest')
save_image(samples_up, 'quick_start.png', nrow=2, padding=4, pad_value=1)
