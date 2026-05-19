from denoising_diffusion_pytorch import Unet, GaussianDiffusion
from torchvision.utils import save_image
import torch

# Build the U-Net and diffusion pipeline
model = Unet(dim=64, dim_mults=(1, 2, 4, 8), channels=3)
diffusion = GaussianDiffusion(
    model, image_size=64, timesteps=1000, sampling_timesteps=250
)

# Load pre-trained weights
checkpoint = torch.load('models/ddpm_african_fabrics.pt', map_location='cpu')
ema_state = checkpoint['ema']
state_dict = {k.replace('ema_model.', ''): v
              for k, v in ema_state.items() if k.startswith('ema_model.')}
diffusion.load_state_dict(state_dict)
diffusion.eval()

# Generate 4 fabric patterns from pure noise
with torch.no_grad():
    samples = diffusion.sample(batch_size=4)
# samples shape: [4, 3, 64, 64] -- values in [-1, 1]

# Upscale from 64x64 to 256x256 for better viewing quality
samples_upscaled = torch.nn.functional.interpolate(
    samples, scale_factor=4, mode='nearest'
)
save_image(samples_upscaled, 'quick_start_output.png', nrow=2,
           padding=4, pad_value=1)
print("Saved quick_start_output.png")