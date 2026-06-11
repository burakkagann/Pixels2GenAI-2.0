
import numpy as np
from PIL import Image
from scipy.ndimage import convolve

# Initialize 128x128 grid with two chemical concentrations
size = 128
chemical_u = np.ones((size, size))  # Chemical U starts at 1 everywhere
chemical_v = np.zeros((size, size))  # Chemical V starts at 0

# Add small random perturbation to trigger pattern formation
center_region = slice(60, 68)
chemical_v[center_region, center_region] = np.random.random((8, 8)) * 0.5

# Gray-Scott parameters for spot patterns
feed_rate = 0.055    # How fast U is replenished
kill_rate = 0.062    # How fast V is removed
diffusion_u = 0.16   # How fast U spreads
diffusion_v = 0.08   # How fast V spreads

# Laplacian kernel for diffusion calculation
laplacian_kernel = np.array([[0.05, 0.2, 0.05],
                            [0.2, -1.0, 0.2],
                            [0.05, 0.2, 0.05]])

# Run one step of Gray-Scott reaction-diffusion
laplacian_u = convolve(chemical_u, laplacian_kernel, mode='wrap')
laplacian_v = convolve(chemical_v, laplacian_kernel, mode='wrap')

# Apply reaction-diffusion equations
reaction_term = chemical_u * chemical_v * chemical_v
chemical_u += diffusion_u * laplacian_u - reaction_term + feed_rate * (1 - chemical_u)
chemical_v += diffusion_v * laplacian_v + reaction_term - (feed_rate + kill_rate) * chemical_v

# Convert V concentration to grayscale image (patterns appear in V)
pattern_image = (chemical_v * 255).astype(np.uint8)
result_image = Image.fromarray(pattern_image)
result_image.save('gray_scott_basic.png')
