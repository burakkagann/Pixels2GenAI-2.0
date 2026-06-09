
import numpy as np
from PIL import Image, ImageDraw

def create_kaleidoscope(size, num_folds, seed_pattern="gradient"):
    center = size // 2
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    # Create coordinate grids
    y, x = np.ogrid[:size, :size]
    x_centered = x - center
    y_centered = y - center

    # Calculate polar coordinates
    angle = np.arctan2(y_centered, x_centered)
    radius = np.sqrt(x_centered**2 + y_centered**2)

    # Wedge angle for N-fold symmetry
    wedge_angle = 2 * np.pi / num_folds

    # Map all angles to a single wedge with reflection
    angle_positive = angle + np.pi
    wedge_index = (angle_positive / wedge_angle).astype(int)
    angle_in_wedge = angle_positive - wedge_index * wedge_angle

    # Mirror odd-numbered wedges for reflection symmetry
    is_odd = wedge_index % 2 == 1
    angle_mirrored = np.where(is_odd, wedge_angle - angle_in_wedge, angle_in_wedge)

    # Create source pattern based on mirrored coordinates
    # Use different frequencies for visual interest
    freq_scale = 3 + num_folds / 4  # Vary pattern with fold count

    red = ((np.sin(angle_mirrored * freq_scale + radius * 0.08) + 1) * 100 + 50).astype(np.uint8)
    green = ((np.cos(angle_mirrored * (freq_scale + 1) + radius * 0.05) + 1) * 100 + 50).astype(np.uint8)
    blue = ((np.sin(radius * 0.1 - angle_mirrored * 2) + 1) * 100 + 50).astype(np.uint8)

    # Apply circular mask
    in_circle = radius < center - 5

    canvas[in_circle, 0] = red[in_circle]
    canvas[in_circle, 1] = green[in_circle]
    canvas[in_circle, 2] = blue[in_circle]

    return canvas

# Configuration
panel_size = 280
spacing = 15
label_height = 25

# Total canvas size for 2x2 grid with labels
total_width = panel_size * 2 + spacing * 3
total_height = panel_size * 2 + spacing * 3 + label_height * 2

# Create canvas with white background
canvas = np.ones((total_height, total_width, 3), dtype=np.uint8) * 255

# Generate kaleidoscopes with different fold counts
fold_counts = [4, 6, 8, 12]
positions = [
    (spacing, spacing + label_height),                              # Top-left
    (spacing * 2 + panel_size, spacing + label_height),             # Top-right
    (spacing, spacing * 2 + panel_size + label_height * 2),         # Bottom-left
    (spacing * 2 + panel_size, spacing * 2 + panel_size + label_height * 2)  # Bottom-right
]

for folds, (x_pos, y_pos) in zip(fold_counts, positions):
    kaleidoscope = create_kaleidoscope(panel_size, folds)
    canvas[y_pos:y_pos+panel_size, x_pos:x_pos+panel_size] = kaleidoscope

# Convert to PIL Image for adding labels
output_image = Image.fromarray(canvas)
draw = ImageDraw.Draw(output_image)

# Add labels for each panel
labels = ["4-fold Symmetry", "6-fold Symmetry", "8-fold Symmetry", "12-fold Symmetry"]
label_positions = [
    (spacing + panel_size // 2, spacing),
    (spacing * 2 + panel_size + panel_size // 2, spacing),
    (spacing + panel_size // 2, spacing * 2 + panel_size + label_height),
    (spacing * 2 + panel_size + panel_size // 2, spacing * 2 + panel_size + label_height)
]

for label, (lx, ly) in zip(labels, label_positions):
    bbox = draw.textbbox((0, 0), label)
    text_width = bbox[2] - bbox[0]
    draw.text((lx - text_width // 2, ly), label, fill=(0, 0, 0))

# Add title at the very top (optional, can be trimmed)
# draw.text((total_width // 2 - 100, 5), "Kaleidoscope Variations", fill=(50, 50, 50))

# Save the comparison grid
output_image.save('kaleidoscope_variations.png')
