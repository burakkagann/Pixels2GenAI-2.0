import numpy as np
import matplotlib.pyplot as plt

def angle_to_rgb(angle):
    """Convert angle (radians) to RGB color using color wheel."""
    hue = ((angle + np.pi) / (2 * np.pi) * 255).astype(np.uint8)

    image = np.zeros((*hue.shape, 3), dtype=np.uint8)
    segment = hue // 43
    remainder = (hue % 43) * 6

    image[:, :, 0] = np.where(segment == 0, 255,
                     np.where(segment == 1, 255 - remainder,
                     np.where(segment == 2, 0,
                     np.where(segment == 3, 0,
                     np.where(segment == 4, remainder, 255)))))

    image[:, :, 1] = np.where(segment == 0, remainder,
                     np.where(segment == 1, 255,
                     np.where(segment == 2, 255,
                     np.where(segment == 3, 255 - remainder,
                     np.where(segment == 4, 0, 0)))))

    image[:, :, 2] = np.where(segment == 0, 0,
                     np.where(segment == 1, 0,
                     np.where(segment == 2, remainder,
                     np.where(segment == 3, 255,
                     np.where(segment == 4, 255, 255 - remainder)))))

    return image

# Create coordinate system
size = 256
center = size // 2
y_coords, x_coords = np.ogrid[:size, :size]

# Calculate relative coordinates from center
rel_x = x_coords - center
rel_y = y_coords - center

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(10, 10))

# 1. Radial Inward (points toward center)
dx_in = -rel_x  # Negative because pointing toward center
dy_in = -rel_y
angle_in = np.arctan2(dy_in, dx_in)
img_in = angle_to_rgb(angle_in)
axes[0, 0].imshow(img_in)
axes[0, 0].set_title('Radial Inward\n(toward center)', fontsize=12, fontweight='bold')
axes[0, 0].plot(center, center, 'ko', markersize=6)
axes[0, 0].axis('off')

# 2. Radial Outward (points away from center)
dx_out = rel_x
dy_out = rel_y
angle_out = np.arctan2(dy_out, dx_out)
img_out = angle_to_rgb(angle_out)
axes[0, 1].imshow(img_out)
axes[0, 1].set_title('Radial Outward\n(away from center)', fontsize=12, fontweight='bold')
axes[0, 1].plot(center, center, 'ko', markersize=6)
axes[0, 1].axis('off')

# 3. Rotational (perpendicular to radial - circular flow)
# To get perpendicular: swap components and negate one
dx_rot = -rel_y  # Perpendicular: (dx, dy) -> (-dy, dx)
dy_rot = rel_x
angle_rot = np.arctan2(dy_rot, dx_rot)
img_rot = angle_to_rgb(angle_rot)
axes[1, 0].imshow(img_rot)
axes[1, 0].set_title('Rotational\n(circular flow)', fontsize=12, fontweight='bold')
axes[1, 0].plot(center, center, 'ko', markersize=6)
axes[1, 0].axis('off')

# 4. Uniform Diagonal (same direction everywhere)
dx_uni = np.ones_like(rel_x)
dy_uni = np.ones_like(rel_y)
angle_uni = np.arctan2(dy_uni, dx_uni)  # Constant 45 degrees
img_uni = angle_to_rgb(angle_uni)
axes[1, 1].imshow(img_uni)
axes[1, 1].set_title('Uniform Diagonal\n(constant direction)', fontsize=12, fontweight='bold')
axes[1, 1].axis('off')

# Add overall title
fig.suptitle('Four Common Vector Field Patterns',
             fontsize=16, fontweight='bold')

plt.tight_layout()
plt.savefig('vector_field_variations.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()

