import torch
from facades_generator import create_facades_generator
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

# Load pre-trained facades U-Net generator
generator = create_facades_generator('checkpoints/generator_weights.pth')
generator.eval()

# Load a CMP Facades segmentation label
label = Image.open('sample_facades/base/cmp_b0001.png').convert('RGB').resize((256, 256))
label_arr = np.array(label).astype(np.float32) / 255.0
x = torch.from_numpy((label_arr - 0.5) / 0.5).permute(2, 0, 1).unsqueeze(0)

with torch.no_grad():
    facade = generator(x)

facade = ((facade.squeeze().permute(1, 2, 0).numpy() + 1) / 2).clip(0, 1)
plt.imsave('quick_start_output.png', facade)
