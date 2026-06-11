import numpy as np
from PIL import Image

def create_mandala_ring(size, inner_radius, outer_radius, num_folds, color_scheme):
    center = size // 2
    ring = np.zeros((size, size, 3), dtype=np.uint8)

    # Create coordinate grids
    y, x = np.ogrid[:size, :size]
    x_centered = x - center
    y_centered = y - center

    # Calculate polar coordinates
    angle = np.arctan2(y_centered, x_centered)
    radius = np.sqrt(x_centered**2 + y_centered**2)

    # Solution to TODO 1: Calculate wedge angle
    # For N-fold symmetry, each wedge spans (2 * pi / N) radians
    wedge_angle = 2 * np.pi / num_folds

    # Map angles to single wedge with reflection
    angle_positive = angle + np.pi
    wedge_index = (angle_positive / wedge_angle).astype(int)
    angle_in_wedge = angle_positive - wedge_index * wedge_angle

    # Mirror odd-numbered wedges for reflection symmetry
    is_odd = wedge_index % 2 == 1
    angle_mirrored = np.where(is_odd, wedge_angle - angle_in_wedge, angle_in_wedge)

    # Solution to TODO 2: Create the ring mask
    # Include pixels where inner_radius <= radius < outer_radius
    in_ring = (radius >= inner_radius) & (radius < outer_radius)

    # Solution to TODO 3: Calculate colors
    # Use color_scheme multipliers and trigonometric functions for gradients
    r_mult, g_mult, b_mult = color_scheme

    # Normalize radius within the ring for smooth color transitions
    ring_position = (radius - inner_radius) / max(outer_radius - inner_radius, 1)

    # Create color patterns using angle and radius
    red = ((np.sin(angle_mirrored * num_folds + ring_position * np.pi * 2) + 1) * 100 * r_mult + 30).astype(np.uint8)
    green = ((np.cos(angle_mirrored * (num_folds + 2) - ring_position * np.pi) + 1) * 100 * g_mult + 30).astype(np.uint8)
    blue = ((np.sin(ring_position * np.pi * 3 + angle_mirrored * 2) + 1) * 100 * b_mult + 30).astype(np.uint8)

    # Apply colors to ring pixels
    ring[in_ring, 0] = red[in_ring]
    ring[in_ring, 1] = green[in_ring]
    ring[in_ring, 2] = blue[in_ring]

    return ring, in_ring

def create_mandala(size, ring_specs):
    """
    Create a complete mandala from multiple rings.

    Parameters:
        size: Image dimensions
        ring_specs: List of (inner_r, outer_r, folds, color_scheme) tuples

    Returns:
        Complete mandala image array
    """
    canvas = np.zeros((size, size, 3), dtype=np.uint8)

    # Solution to TODO 4: Composite all rings
    for inner_r, outer_r, folds, colors in ring_specs:
        ring, mask = create_mandala_ring(size, inner_r, outer_r, folds, colors)
        # Use mask to add ring without overwriting existing content
        canvas[mask] = ring[mask]

    return canvas

# Main program
if __name__ == "__main__":
    size = 512
    center = size // 2

    # Solution to TODO 5: Define ring specifications
    # Each ring: (inner_radius, outer_radius, num_folds, (r, g, b multipliers))
    # Create a visually appealing mandala with varying symmetry
    ring_specs = [
        # Center circle - high fold count for intricate center
        (0, 40, 12, (1.0, 0.6, 0.8)),

        # Inner ring - moderate folds
        (40, 80, 8, (0.7, 1.0, 0.5)),

        # Middle ring - classic 6-fold like traditional kaleidoscope
        (80, 130, 6, (0.5, 0.8, 1.0)),

        # Outer ring - lower fold count for larger segments
        (130, 180, 4, (1.0, 0.5, 0.6)),

        # Edge ring - back to higher folds for fine detail
        (180, 240, 10, (0.6, 0.9, 0.7)),
    ]

    # Create and save the mandala
    mandala = create_mandala(size, ring_specs)

    output = Image.fromarray(mandala, mode='RGB')
    output.save('mandala_pattern.png')
