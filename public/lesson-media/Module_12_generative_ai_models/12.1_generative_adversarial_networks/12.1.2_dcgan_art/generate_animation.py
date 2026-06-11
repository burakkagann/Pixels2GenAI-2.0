"""
Generate Animated GIF from Trained DCGAN

Creates a 15-second looping animation showing smooth transitions through
latent space, demonstrating the Generator's ability to create diverse
African fabric-style patterns.

Usage:
    python generate_animation.py

Output:
    dcgan_fabric_animation.gif (15 seconds, 10 fps, 150 frames)
"""

import os
import torch
import numpy as np
import imageio.v2 as imageio
from dcgan_model import Generator, LATENT_DIM


def linear_interpolate(z1, z2, steps):
    """
    Interpolate between two latent vectors.

    Args:
        z1: Starting latent vector (shape: LATENT_DIM)
        z2: Ending latent vector (shape: LATENT_DIM)
        steps: Number of interpolation steps

    Returns:
        List of interpolated latent vectors
    """
    interpolated = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        z_interp = (1 - t) * z1 + t * z2
        interpolated.append(z_interp)
    return interpolated


def generate_frames(generator, latent_vectors, device='cpu'):
    """
    Generate image frames from latent vectors.

    Args:
        generator: Trained Generator model
        latent_vectors: List of latent vectors (each shape: LATENT_DIM)
        device: 'cpu' or 'cuda'

    Returns:
        List of numpy arrays (H, W, 3) in uint8 format
    """
    frames = []
    generator.eval()

    with torch.no_grad():
        for z in latent_vectors:
            # Reshape to (1, LATENT_DIM, 1, 1) for generator input
            z_input = z.view(1, LATENT_DIM, 1, 1).to(device)

            # Generate image
            img_tensor = generator(z_input)

            # Convert from [-1, 1] to [0, 1]
            img_tensor = (img_tensor + 1) / 2
            img_tensor = img_tensor.clamp(0, 1)

            # Convert to numpy (H, W, C) format
            img_np = img_tensor[0].permute(1, 2, 0).cpu().numpy()

            # Convert to uint8 (0-255)
            img_uint8 = (img_np * 255).astype(np.uint8)

            frames.append(img_uint8)

    return frames


def create_animation(model_path='exercise3_generator.pth',
                     num_keypoints=5,
                     frames_per_segment=38,
                     fps=10,
                     seed=42):
    """
    Create looping animation through latent space.

    Args:
        model_path: Path to trained generator weights
        num_keypoints: Number of keypoints in latent space (includes loop back)
        frames_per_segment: Frames between each keypoint
        fps: Frames per second for output GIF
        seed: Random seed for reproducibility

    Returns:
        List of frames (numpy arrays)
    """
    print("=" * 60)
    print("DCGAN Animation Generator")
    print("=" * 60)
    print(f"Model: {model_path}")
    print(f"Keypoints: {num_keypoints}")
    print(f"Frames per segment: {frames_per_segment}")
    print(f"FPS: {fps}")
    print()

    # Load generator
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    generator = Generator().to(device)

    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' not found!")
        print("Please ensure you've trained the model first (exercise3_train.py)")
        return None

    generator.load_state_dict(torch.load(model_path, map_location=device))
    generator.eval()
    print(f"[OK] Loaded model from {model_path}")
    print(f"[OK] Using device: {device}")
    print()

    # Generate keypoints in latent space
    torch.manual_seed(seed)
    keypoints = [torch.randn(LATENT_DIM) for _ in range(num_keypoints)]

    # Add first keypoint at end to create seamless loop
    keypoints.append(keypoints[0])

    print(f"Generating {num_keypoints} keypoints...")

    # Generate interpolated latent vectors
    all_latent_vectors = []
    for i in range(len(keypoints) - 1):
        segment_vectors = linear_interpolate(
            keypoints[i],
            keypoints[i + 1],
            frames_per_segment
        )

        # Avoid duplicate frames at segment boundaries
        if i < len(keypoints) - 2:
            all_latent_vectors.extend(segment_vectors[:-1])
        else:
            all_latent_vectors.extend(segment_vectors)

        print(f"  Segment {i+1}/{num_keypoints}: {len(segment_vectors)} frames")

    print(f"\nTotal frames: {len(all_latent_vectors)}")
    print(f"Duration: {len(all_latent_vectors) / fps:.1f} seconds")
    print()

    # Generate image frames
    print("Generating image frames...")
    frames = generate_frames(generator, all_latent_vectors, device)
    print(f"[OK] Generated {len(frames)} frames")

    return frames


def save_gif(frames, output_path='dcgan_fabric_animation.gif', fps=10):
    """
    Save frames as animated GIF.

    Args:
        frames: List of numpy arrays (H, W, 3) in uint8
        output_path: Output filename
        fps: Frames per second
    """
    print(f"\nSaving GIF to {output_path}...")
    imageio.mimsave(
        output_path,
        frames,
        fps=fps,
        loop=0  # 0 = infinite loop
    )

    # Get file size
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[OK] Saved {output_path}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Frames: {len(frames)}")
    print(f"  FPS: {fps}")
    print(f"  Duration: {len(frames) / fps:.1f} seconds")

    if file_size_mb > 3:
        print(f"\n[WARNING] File size ({file_size_mb:.2f} MB) exceeds 3 MB")
        print("  Consider reducing frames_per_segment or using lower quality")


if __name__ == '__main__':
    # Generate animation
    frames = create_animation(
        model_path='exercise3_generator.pth',
        num_keypoints=5,
        frames_per_segment=38,
        fps=10,
        seed=42
    )

    if frames is not None:
        # Save as GIF
        save_gif(frames, 'dcgan_fabric_animation.gif', fps=10)
        print("\n" + "=" * 60)
        print("Animation generation complete!")
        print("=" * 60)
