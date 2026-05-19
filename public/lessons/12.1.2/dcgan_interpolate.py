"""
Latent space interpolation for DCGAN-generated images.

Demonstrates smooth transitions between generated images by interpolating
between points in the latent space.

Based on PyTorch Official DCGAN Tutorial:
https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html
"""

import os
import numpy as np
import torch
import matplotlib.pyplot as plt
import imageio.v2 as imageio

from dcgan_model import Generator, LATENT_DIM


def linear_interpolate(z1, z2, t):
    """
    Linear interpolation between two latent vectors.

    Args:
        z1: Starting latent vector
        z2: Ending latent vector
        t: Interpolation parameter in [0, 1] (0=z1, 1=z2)

    Returns:
        Interpolated latent vector
    """
    return (1 - t) * z1 + t * z2


def generate_interpolation_frames(generator, z_start, z_end, num_frames=30):
    """
    Generate frames for smooth interpolation animation.

    Args:
        generator: Trained Generator model
        z_start: Starting latent vector
        z_end: Ending latent vector
        num_frames: Number of frames to generate

    Returns:
        List of image frames as numpy arrays
    """
    frames = []

    generator.eval()
    with torch.no_grad():
        for i in range(num_frames):
            # Calculate interpolation parameter
            t = i / (num_frames - 1) if num_frames > 1 else 0

            # Interpolate in latent space
            z_interp = linear_interpolate(z_start, z_end, t)
            z_interp = z_interp.view(1, LATENT_DIM, 1, 1)

            # Generate image
            img = generator(z_interp)

            # Convert to displayable format
            img = (img + 1) / 2  # [-1, 1] -> [0, 1]
            img = img.clamp(0, 1)
            img = img[0].permute(1, 2, 0).numpy()  # CHW -> HWC
            img = (img * 255).astype(np.uint8)

            frames.append(img)

    return frames


def create_interpolation_animation(generator, num_keypoints=4, frames_per_segment=20,
                                    seed=42):
    """
    Create a looping animation that interpolates through multiple latent points.

    Args:
        generator: Trained Generator model
        num_keypoints: Number of random latent vectors to interpolate between
        frames_per_segment: Frames between each keypoint pair
        seed: Random seed for reproducibility

    Returns:
        List of frames for the animation
    """
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Generate random keypoints in latent space
    keypoints = [torch.randn(LATENT_DIM) for _ in range(num_keypoints)]

    # Add first point at end to create a loop
    keypoints.append(keypoints[0])

    all_frames = []

    print(f"Generating {num_keypoints} segments...")
    for i in range(len(keypoints) - 1):
        z_start = keypoints[i]
        z_end = keypoints[i + 1]

        frames = generate_interpolation_frames(
            generator, z_start, z_end,
            num_frames=frames_per_segment
        )

        # Don't add the last frame (except for final segment) to avoid duplicates
        if i < len(keypoints) - 2:
            all_frames.extend(frames[:-1])
        else:
            all_frames.extend(frames)

        print(f"  Segment {i+1}/{num_keypoints} complete")

    return all_frames


def create_interpolation_strip(generator, num_steps=8, seed=42):
    """
    Create a static image showing interpolation steps between two points.

    Args:
        generator: Trained Generator model
        num_steps: Number of interpolation steps to show
        seed: Random seed for reproducibility

    Returns:
        matplotlib Figure object
    """
    torch.manual_seed(seed)

    z_start = torch.randn(LATENT_DIM)
    z_end = torch.randn(LATENT_DIM)

    fig, axes = plt.subplots(1, num_steps, figsize=(num_steps * 2, 2.5))

    generator.eval()
    with torch.no_grad():
        for i, ax in enumerate(axes):
            t = i / (num_steps - 1)
            z = linear_interpolate(z_start, z_end, t)
            z = z.view(1, LATENT_DIM, 1, 1)

            img = generator(z)
            img = (img + 1) / 2
            img = img.clamp(0, 1)
            img = img[0].permute(1, 2, 0).numpy()

            ax.imshow(img)
            ax.axis('off')
            ax.set_title(f't={t:.2f}', fontsize=10)

    plt.suptitle('Latent Space Interpolation\n(z_start → z_end)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()

    return fig


def load_pretrained_generator(weights_path='generator_weights.pth'):
    """Load a pre-trained generator model."""
    generator = Generator()

    if os.path.exists(weights_path):
        generator.load_state_dict(torch.load(weights_path, map_location='cpu'))
        print(f"Loaded pre-trained weights from {weights_path}")
    else:
        print(f"Note: Pre-trained weights not found at {weights_path}")
        print("Using randomly initialized generator (results will be noise).")
        print("Run 'python dcgan_train.py' first to train the model.")

    return generator


def main():
    """Main function to create interpolation visualizations."""
    print("=" * 50)
    print("DCGAN Latent Space Interpolation")
    print("=" * 50)

    # Load the generator
    generator = load_pretrained_generator()

    # Create interpolation strip (static image)
    print("\nCreating interpolation strip...")
    fig = create_interpolation_strip(generator, num_steps=8, seed=42)
    fig.savefig('interpolation_strip.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Saved interpolation_strip.png")

    # Create animation
    print("\nCreating interpolation animation...")
    frames = create_interpolation_animation(
        generator,
        num_keypoints=4,
        frames_per_segment=15,
        seed=42
    )

    # Save as GIF
    gif_path = 'latent_interpolation.gif'
    imageio.mimsave(gif_path, frames, fps=15, loop=0)
    print(f"Saved {gif_path} ({len(frames)} frames)")

    print("\nDone! Check the generated files:")
    print("  - interpolation_strip.png: Static interpolation steps")
    print("  - latent_interpolation.gif: Animated morphing between patterns")


if __name__ == '__main__':
    main()
