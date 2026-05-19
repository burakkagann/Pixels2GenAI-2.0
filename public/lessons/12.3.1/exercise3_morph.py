import torch
import numpy as np
from generate_ddpm_morph import (
    generate_from_noise,
    load_model_from_checkpoint,
    find_latest_checkpoint,
    upscale_image,
    create_gif,
)

# =============================================================================
# CONFIG -- Experiment with these values after completing the TODOs below
# =============================================================================

SEED_A = 42           # First pattern seed (try: 7, 99, 256, 500)
SEED_B = 123          # Second pattern seed (try: 42, 77, 300, 999)
NUM_FRAMES = 20       # Animation frames (try: 8=choppy, 30=smooth, 60=very smooth)
FPS = 8               # Playback speed (try: 5=slow-mo, 12=natural, 20=fast)
OUTPUT_SIZE = 256     # Output resolution (try: 128=small/fast, 512=high-res/slow)

# Do not change these -- must match the trained model
IMAGE_SIZE = 64
OUTPUT_PATH = 'my_morph.gif'

# =============================================================================
# Step 1: Load the trained model (provided -- no changes needed)
# =============================================================================

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

checkpoint_path = find_latest_checkpoint()
diffusion = load_model_from_checkpoint(checkpoint_path, device)

# =============================================================================
# Step 2: Create two noise vectors from your chosen seeds (provided)
# =============================================================================

# Noise vector A: set seed for reproducibility, then draw random noise
# torch.manual_seed locks the random generator so we get the same pattern
# torch.randn draws from a standard normal distribution (like np.random.randn)
torch.manual_seed(SEED_A)
noise_a = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)

# Noise vector B: same process, different seed produces a different pattern
torch.manual_seed(SEED_B)
noise_b = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)

print(f"Noise A shape: {noise_a.shape}  (seed={SEED_A})")
print(f"Noise B shape: {noise_b.shape}  (seed={SEED_B})")

# =============================================================================
# Step 3: Blend the two noise vectors and generate a frame for each blend
# =============================================================================

# TODO 1: Create NUM_FRAMES evenly-spaced blend values from 0.0 to 1.0
# np.linspace(start, stop, count) creates 'count' values equally spaced
# between 'start' and 'stop'. Example: np.linspace(0, 1, 5) → [0, 0.25, 0.5, 0.75, 1.0]
blend_values = ...

print(f"\nGenerating {NUM_FRAMES} frames...")
frames = []

for t in blend_values:
    # TODO 2: Compute blended noise using linear interpolation
    # Formula: blended = (1 - t) * noise_a + t * noise_b
    # When t=0.0, you get 100% noise_a. When t=1.0, you get 100% noise_b.
    # When t=0.5, you get a 50/50 mix of both.
    blended_noise = ...

    # Generate image from blended noise (provided helper -- no changes needed)
    image = generate_from_noise(diffusion, blended_noise, device)
    image = upscale_image(image, OUTPUT_SIZE)
    frames.append(image)
    print(f"  Frame {len(frames)}/{NUM_FRAMES} (blend={t:.2f})")

# =============================================================================
# Step 4: Save as animated GIF (provided -- no changes needed)
# =============================================================================

create_gif(frames, OUTPUT_PATH, FPS)
print(f"\nAnimation saved to {OUTPUT_PATH}")
print(f"Try changing SEED_A, SEED_B, NUM_FRAMES, or FPS in the CONFIG section!")
