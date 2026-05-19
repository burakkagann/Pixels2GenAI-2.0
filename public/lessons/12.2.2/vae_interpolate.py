import torch
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio

from vae_model import VAE, LATENT_DIM

def linear_interpolate(z1, z2, t):
    """
    Linear interpolation between two latent vectors.

    The simplest interpolation method: follows a straight line path
    from z1 to z2 in latent space.

    Args:
        z1: Starting latent vector
        z2: Ending latent vector
        t: Interpolation parameter in [0, 1]
           t=0 returns z1, t=1 returns z2

    Returns:
        Interpolated latent vector
    """
    return (1 - t) * z1 + t * z2

def slerp(z1, z2, t):
    """
    Spherical linear interpolation between two latent vectors.

    Slerp follows a great circle path on the hypersphere, which is more
    geometrically meaningful for normalized vectors. This can produce
    smoother transitions in high-dimensional latent spaces.

    Originally developed for quaternion interpolation in animation
    (Shoemake, 1985).

    Args:
        z1: Starting latent vector
        z2: Ending latent vector
        t: Interpolation parameter in [0, 1]

    Returns:
        Interpolated latent vector
    """
    # Normalize vectors
    z1_norm = z1 / (torch.norm(z1) + 1e-8)
    z2_norm = z2 / (torch.norm(z2) + 1e-8)

    # Calculate angle between vectors
    dot_product = torch.sum(z1_norm * z2_norm)
    dot_product = torch.clamp(dot_product, -1.0, 1.0)
    omega = torch.acos(dot_product)

    # If vectors are nearly identical, fall back to linear
    if omega < 1e-6:
        return linear_interpolate(z1, z2, t)

    # Spherical interpolation formula
    sin_omega = torch.sin(omega)
    coefficient_1 = torch.sin((1 - t) * omega) / sin_omega
    coefficient_2 = torch.sin(t * omega) / sin_omega

    return coefficient_1 * z1 + coefficient_2 * z2

def generate_interpolation_frames(decoder, z_start, z_end, num_frames=30,
                                   method='linear'):
    """
    Generate frames for smooth interpolation animation.

    Args:
        decoder: VAE decoder network
        z_start: Starting latent vector
        z_end: Ending latent vector
        num_frames: Number of frames to generate
        method: 'linear' or 'slerp'

    Returns:
        List of image frames as numpy arrays (H, W, 3) in uint8 format
    """
    frames = []
    interpolate_fn = slerp if method == 'slerp' else linear_interpolate

    with torch.no_grad():
        for i in range(num_frames):
            # Calculate interpolation parameter
            t = i / (num_frames - 1) if num_frames > 1 else 0

            # Interpolate in latent space
            z_interp = interpolate_fn(z_start, z_end, t)
            z_interp = z_interp.unsqueeze(0)  # Add batch dimension

            # Decode to image
            image = decoder(z_interp)

            # Convert to displayable format
            image = (image + 1) / 2  # [-1, 1] -> [0, 1]
            image = image.clamp(0, 1)
            image = image[0].permute(1, 2, 0).numpy()  # CHW -> HWC
            image = (image * 255).astype(np.uint8)

            frames.append(image)

    return frames

def create_interpolation_strip(decoder, num_steps=8, seed=42):
    """
    Create a static image showing interpolation steps between two points.

    This visualization shows discrete steps from one pattern to another,
    making it easy to observe how the image gradually transforms.

    Args:
        decoder: VAE decoder network
        num_steps: Number of interpolation steps to show
        seed: Random seed for reproducibility

    Returns:
        matplotlib Figure object
    """
    torch.manual_seed(seed)

    z_start = torch.randn(LATENT_DIM)
    z_end = torch.randn(LATENT_DIM)

    fig, axes = plt.subplots(1, num_steps, figsize=(num_steps * 2, 2.5))

    with torch.no_grad():
        for i, ax in enumerate(axes):
            t = i / (num_steps - 1)
            z = linear_interpolate(z_start, z_end, t)
            z = z.unsqueeze(0)

            image = decoder(z)
            image = (image + 1) / 2
            image = image.clamp(0, 1)
            image = image[0].permute(1, 2, 0).numpy()

            ax.imshow(image)
            ax.axis('off')
            ax.set_title(f't={t:.2f}', fontsize=10)

    plt.suptitle('Latent Space Interpolation (z_start → z_end)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()

    return fig

def create_looping_animation(decoder, num_keypoints=4, frames_per_segment=15,
                              method='linear', seed=42):
    """
    Create a looping animation that interpolates through multiple latent points.

    The animation visits each keypoint in sequence and returns to the start,
    creating a seamless loop.

    Args:
        decoder: VAE decoder network
        num_keypoints: Number of random latent vectors to visit
        frames_per_segment: Frames between each keypoint pair
        method: 'linear' or 'slerp'
        seed: Random seed for reproducibility

    Returns:
        List of frames for the animation
    """
    torch.manual_seed(seed)

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
            decoder, z_start, z_end,
            num_frames=frames_per_segment,
            method=method
        )

        # Avoid duplicate frames at segment boundaries
        if i < len(keypoints) - 2:
            all_frames.extend(frames[:-1])
        else:
            all_frames.extend(frames)

        print(f"  Segment {i+1}/{num_keypoints} complete")

    return all_frames

def compare_interpolation_methods(decoder, seed=42):
    """
    Create a comparison visualization of linear vs slerp interpolation.

    Args:
        decoder: VAE decoder network
        seed: Random seed for reproducibility

    Returns:
        matplotlib Figure object
    """
    torch.manual_seed(seed)

    z_start = torch.randn(LATENT_DIM)
    z_end = torch.randn(LATENT_DIM)

    num_steps = 5
    fig, axes = plt.subplots(2, num_steps, figsize=(num_steps * 2, 4.5))

    with torch.no_grad():
        for i in range(num_steps):
            t = i / (num_steps - 1)

            # Linear interpolation
            z_linear = linear_interpolate(z_start, z_end, t).unsqueeze(0)
            img_linear = decoder(z_linear)
            img_linear = (img_linear + 1) / 2
            img_linear = img_linear.clamp(0, 1)[0].permute(1, 2, 0).numpy()

            # Spherical interpolation
            z_slerp = slerp(z_start, z_end, t).unsqueeze(0)
            img_slerp = decoder(z_slerp)
            img_slerp = (img_slerp + 1) / 2
            img_slerp = img_slerp.clamp(0, 1)[0].permute(1, 2, 0).numpy()

            axes[0, i].imshow(img_linear)
            axes[0, i].axis('off')
            if i == 0:
                axes[0, i].set_ylabel('Linear', fontsize=11)

            axes[1, i].imshow(img_slerp)
            axes[1, i].axis('off')
            if i == 0:
                axes[1, i].set_ylabel('Slerp', fontsize=11)

            axes[0, i].set_title(f't={t:.2f}', fontsize=10)

    plt.suptitle('Linear vs Spherical (Slerp) Interpolation',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()

    return fig

def load_pretrained_vae(weights_path='vae_weights.pth'):
    """Load a pre-trained VAE model."""
    vae = VAE(latent_dim=LATENT_DIM)

    try:
        vae.load_state_dict(torch.load(weights_path, map_location='cpu'))
        print(f"Loaded pre-trained weights from {weights_path}")
    except FileNotFoundError:
        print(f"Warning: {weights_path} not found. Using random weights.")
        print("Run 'python vae_train.py' first to train the model.")

    vae.eval()
    return vae

def main():
    """Main function to create interpolation visualizations."""
    print("=" * 50)
    print("VAE Latent Space Interpolation")
    print("=" * 50)

    # Load the VAE
    vae = load_pretrained_vae()
    decoder = vae.decoder

    # Create interpolation strip (static image)
    print("\nCreating interpolation strip...")
    fig = create_interpolation_strip(decoder, num_steps=8, seed=42)
    fig.savefig('interpolation_strip.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Saved interpolation_strip.png")

    # Create comparison image
    print("\nCreating interpolation comparison...")
    fig = compare_interpolation_methods(decoder, seed=42)
    fig.savefig('interpolation_comparison.png', dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print("Saved interpolation_comparison.png")

    # Create looping animation
    print("\nCreating interpolation animation...")
    frames = create_looping_animation(
        decoder,
        num_keypoints=4,
        frames_per_segment=15,
        method='linear',
        seed=42
    )

    # Save as GIF
    gif_path = 'interpolation_animation.gif'
    imageio.mimsave(gif_path, frames, fps=15, loop=0)
    print(f"Saved {gif_path} ({len(frames)} frames)")

    print("\nDone! Generated files:")
    print("  - interpolation_strip.png: Static interpolation steps")
    print("  - interpolation_comparison.png: Linear vs Slerp comparison")
    print("  - interpolation_animation.gif: Animated morphing loop")

if __name__ == '__main__':
    main()
