import numpy as np
from PIL import Image

def create_source_image(size=256):
    """Create a synthetic image with geometric patterns."""
    image = np.zeros((size, size), dtype=np.float64)

    # Create concentric squares
    for i in range(0, size // 2, 20):
        # Draw rectangle outline
        thickness = 3
        # Top edge
        image[i:i+thickness, i:size-i] = 255
        # Bottom edge
        image[size-i-thickness:size-i, i:size-i] = 255
        # Left edge
        image[i:size-i, i:i+thickness] = 255
        # Right edge
        image[i:size-i, size-i-thickness:size-i] = 255

    # Add diagonal lines
    for offset in range(-size, size, 30):
        for i in range(size):
            x = i
            y = i + offset
            if 0 <= y < size:
                image[y, x] = 200

    return image

def apply_glitch_effect(image, seed=42):
    """
    Apply a glitch effect using frequency domain manipulation.

    Techniques used:
    1. Asymmetric masking (different filter for left/right halves)
    2. Random frequency zeroing (creates missing data artifacts)
    3. Partial phase scrambling (distorts structure)
    """
    np.random.seed(seed)
    size = image.shape[0]

    # Step 1: Transform to frequency domain
    fft = np.fft.fft2(image)
    fft_shifted = np.fft.fftshift(fft)

    # Step 2: Create asymmetric glitch mask
    # Left half: keep low frequencies (blur)
    # Right half: keep high frequencies (edges)
    mask = np.zeros((size, size), dtype=np.float64)
    center = size // 2

    for y in range(size):
        for x in range(size):
            dist = np.sqrt((x - center)**2 + (y - center)**2)
            if x < center:
                # Left side: low-pass
                mask[y, x] = 1.0 if dist < 40 else 0.1
            else:
                # Right side: high-pass
                mask[y, x] = 0.1 if dist < 20 else 1.0

    # Step 3: Random frequency zeroing (glitch holes)
    # Randomly zero out some frequency bands
    num_glitches = 15
    for _ in range(num_glitches):
        gx = np.random.randint(0, size)
        gy = np.random.randint(0, size)
        glitch_size = np.random.randint(5, 15)
        # Create rectangular glitch region
        y_start = max(0, gy - glitch_size)
        y_end = min(size, gy + glitch_size)
        x_start = max(0, gx - glitch_size)
        x_end = min(size, gx + glitch_size)
        mask[y_start:y_end, x_start:x_end] *= 0.0

    # Step 4: Apply mask to magnitude, partially scramble phase
    magnitude = np.abs(fft_shifted)
    phase = np.angle(fft_shifted)

    # Add noise to phase in certain regions (creates distortion)
    phase_noise = np.random.uniform(-0.5, 0.5, size=(size, size))
    # Only scramble phase in high-frequency regions
    for y in range(size):
        for x in range(size):
            dist = np.sqrt((x - center)**2 + (y - center)**2)
            if dist > 50:
                phase[y, x] += phase_noise[y, x]

    # Step 5: Reconstruct with modified magnitude and phase
    glitched_fft = (magnitude * mask) * np.exp(1j * phase)

    # Step 6: Transform back to spatial domain
    fft_unshifted = np.fft.ifftshift(glitched_fft)
    result = np.fft.ifft2(fft_unshifted)
    result = np.abs(result)

    # Normalize to 0-255
    result_min, result_max = result.min(), result.max()
    if result_max > result_min:
        result = (result - result_min) / (result_max - result_min) * 255
    return result.astype(np.uint8)

# Create source image
size = 256
source = create_source_image(size)

# Apply glitch effect
glitched = apply_glitch_effect(source, seed=42)

# Create side-by-side comparison
gap = 4
output = np.ones((size, size * 2 + gap), dtype=np.uint8) * 128
output[:, :size] = source.astype(np.uint8)
output[:, size + gap:] = glitched

# Save result
result = Image.fromarray(output, mode='L')
result.save('glitch_art_output.png')

print("Glitch art creation complete!")
print(f"Output saved as 'glitch_art_output.png'")
print(f"\nLeft:  Original geometric pattern")
print(f"Right: Glitched version")
print(f"\nGlitch techniques applied:")
print("  1. Asymmetric filtering (left=blur, right=edges)")
print("  2. Random frequency holes (15 glitch regions)")
print("  3. Phase scrambling in high frequencies")
