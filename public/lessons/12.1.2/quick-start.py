import torch
from dcgan_model import Generator, LATENT_DIM
import matplotlib.pyplot as plt

# Load pre-trained generator
generator = Generator()
generator.load_state_dict(torch.load('generator_weights.pth', map_location='cpu'))
generator.eval()

# Generate 4 random art pieces
z = torch.randn(4, LATENT_DIM, 1, 1)
with torch.no_grad():
    images = generator(z)

# Display the generated art
images = (images + 1) / 2  # Convert from [-1,1] to [0,1]
fig, axes = plt.subplots(1, 4, figsize=(12, 3))
for i, ax in enumerate(axes):
    ax.imshow(images[i].permute(1, 2, 0).numpy())
    ax.axis('off')
plt.savefig('quick_start_output.png', dpi=150)
plt.show()