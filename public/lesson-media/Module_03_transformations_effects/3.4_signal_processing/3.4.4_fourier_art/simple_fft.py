import numpy as np
from PIL import Image

# Step 1: Create a synthetic pattern (checkerboard + diagonal lines)
# This pattern has clear frequency components that are easy to visualize
size = 256
image = np.zeros((size, size), dtype=np.float64)

# Add a checkerboard pattern (creates distinct frequency peaks)
checker_size = 16
for y in range(size):
    for x in range(size):
        if ((x // checker_size) + (y // checker_size)) % 2 == 0:
            image[y, x] = 255

# Step 2: Apply the 2D Fast Fourier Transform
# FFT converts spatial data to frequency domain
fft_result = np.fft.fft2(image)

# Step 3: Shift zero frequency to center for visualization
# Without shift, low frequencies are at corners (hard to interpret)
fft_shifted = np.fft.fftshift(fft_result)

# Step 4: Calculate magnitude spectrum (ignore phase for now)
# We use log scale because frequency magnitudes vary enormously
magnitude = np.abs(fft_shifted)
magnitude_log = np.log1p(magnitude)  # log(1+x) to handle zeros

# Step 5: Normalize to 0-255 for image display
magnitude_normalized = (magnitude_log / magnitude_log.max() * 255).astype(np.uint8)

# Step 6: Create side-by-side comparison
output = np.zeros((size, size * 2), dtype=np.uint8)
output[:, :size] = image.astype(np.uint8)  # Original pattern (left)
output[:, size:] = magnitude_normalized     # Magnitude spectrum (right)

# Save the result
result = Image.fromarray(output, mode='L')
result.save('simple_fft_output.png')

print("FFT visualization complete!")
print(f"Output saved as 'simple_fft_output.png'")
print(f"Left: Original checkerboard pattern ({size}x{size})")
print(f"Right: Frequency magnitude spectrum (log scale)")
print("\nNotice: Bright dots in the spectrum correspond to the")
print("checkerboard's regular spacing pattern.")
