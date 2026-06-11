"""
DCGAN Architecture Diagram Generator.

Creates educational visualization showing Generator and Discriminator
architectures side by side.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


def draw_layer_block(ax, x, y, width, height, label, color, text_size=8):
    """Draw a single layer block with label."""
    rect = patches.FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        facecolor=color, edgecolor='black', linewidth=1.5
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=text_size, fontweight='bold', wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, color='gray'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))


def create_dcgan_diagram():
    """Create the DCGAN architecture diagram."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))

    # Colors for different layer types
    colors = {
        'input': '#E8F5E9',      # Light green
        'conv': '#BBDEFB',       # Light blue
        'deconv': '#FFE0B2',     # Light orange
        'bn': '#F3E5F5',         # Light purple
        'activation': '#FFECB3', # Light yellow
        'output': '#FFCDD2',     # Light red
    }

    # ==================== GENERATOR ====================
    ax1.set_xlim(-1, 11)
    ax1.set_ylim(-1, 13)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('Generator Network\n(Noise → Image)', fontsize=14, fontweight='bold', pad=20)

    # Generator layers (bottom to top)
    gen_layers = [
        ('Latent Vector z\n(100 dim)', 0.5, colors['input']),
        ('Dense → Reshape\n4×4×512', 2.0, colors['deconv']),
        ('ConvTranspose2d\n8×8×256', 4.5, colors['deconv']),
        ('BatchNorm + ReLU', 5.5, colors['bn']),
        ('ConvTranspose2d\n16×16×128', 7.0, colors['deconv']),
        ('BatchNorm + ReLU', 8.0, colors['bn']),
        ('ConvTranspose2d\n32×32×64', 9.5, colors['deconv']),
        ('BatchNorm + ReLU', 10.5, colors['bn']),
        ('ConvTranspose2d\n64×64×3 + Tanh', 12.0, colors['output']),
    ]

    x_center = 5
    for i, (label, y, color) in enumerate(gen_layers):
        draw_layer_block(ax1, x_center, y, 4.5, 1.2, label, color)
        if i > 0:
            draw_arrow(ax1, x_center, gen_layers[i-1][1] + 0.6,
                      x_center, y - 0.6, '#4CAF50')

    # Add size annotations
    ax1.text(-0.5, 0.5, '100', fontsize=9, ha='center', va='center', color='#666')
    ax1.text(-0.5, 2.0, '4×4', fontsize=9, ha='center', va='center', color='#666')
    ax1.text(-0.5, 4.5, '8×8', fontsize=9, ha='center', va='center', color='#666')
    ax1.text(-0.5, 7.0, '16×16', fontsize=9, ha='center', va='center', color='#666')
    ax1.text(-0.5, 9.5, '32×32', fontsize=9, ha='center', va='center', color='#666')
    ax1.text(-0.5, 12.0, '64×64', fontsize=9, ha='center', va='center', color='#666')

    # ==================== DISCRIMINATOR ====================
    ax2.set_xlim(-1, 11)
    ax2.set_ylim(-1, 13)
    ax2.set_aspect('equal')
    ax2.axis('off')
    ax2.set_title('Discriminator Network\n(Image → Real/Fake)', fontsize=14, fontweight='bold', pad=20)

    # Discriminator layers (bottom to top - input image at bottom)
    disc_layers = [
        ('Input Image\n64×64×3', 0.5, colors['input']),
        ('Conv2d + LeakyReLU\n32×32×64', 2.5, colors['conv']),
        ('Conv2d\n16×16×128', 4.5, colors['conv']),
        ('BatchNorm + LeakyReLU', 5.5, colors['bn']),
        ('Conv2d\n8×8×256', 7.0, colors['conv']),
        ('BatchNorm + LeakyReLU', 8.0, colors['bn']),
        ('Conv2d\n4×4×512', 9.5, colors['conv']),
        ('BatchNorm + LeakyReLU', 10.5, colors['bn']),
        ('Conv2d → Sigmoid\n1 (Real/Fake)', 12.0, colors['output']),
    ]

    for i, (label, y, color) in enumerate(disc_layers):
        draw_layer_block(ax2, x_center, y, 4.5, 1.2, label, color)
        if i > 0:
            draw_arrow(ax2, x_center, disc_layers[i-1][1] + 0.6,
                      x_center, y - 0.6, '#F44336')

    # Add size annotations
    ax2.text(10.5, 0.5, '64×64', fontsize=9, ha='center', va='center', color='#666')
    ax2.text(10.5, 2.5, '32×32', fontsize=9, ha='center', va='center', color='#666')
    ax2.text(10.5, 4.5, '16×16', fontsize=9, ha='center', va='center', color='#666')
    ax2.text(10.5, 7.0, '8×8', fontsize=9, ha='center', va='center', color='#666')
    ax2.text(10.5, 9.5, '4×4', fontsize=9, ha='center', va='center', color='#666')
    ax2.text(10.5, 12.0, '1', fontsize=9, ha='center', va='center', color='#666')

    # Add legend
    legend_elements = [
        patches.Patch(facecolor=colors['input'], edgecolor='black', label='Input/Output'),
        patches.Patch(facecolor=colors['deconv'], edgecolor='black', label='Transposed Conv (Upsample)'),
        patches.Patch(facecolor=colors['conv'], edgecolor='black', label='Convolution (Downsample)'),
        patches.Patch(facecolor=colors['bn'], edgecolor='black', label='BatchNorm + Activation'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4,
               fontsize=10, frameon=True, bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)

    # Save the diagram
    output_path = 'dcgan_architecture.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()

    print(f"Architecture diagram saved to {output_path}")
    return output_path


if __name__ == '__main__':
    create_dcgan_diagram()
