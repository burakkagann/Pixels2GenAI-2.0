from stylegan2_pytorch import ModelLoader
import torch

loader = ModelLoader(
    base_dir='./',
    name='african_fabrics',                  # expects models/african_fabrics/model_99.pt
)

noise = torch.randn(4, 512)                  # 4 latent vectors in z-space
images = loader.styles_to_images(loader.noise_to_styles(noise, trunc_psi=0.7))

for i, img in enumerate(images):
    img.save(f'fabric_{i}.png')
