"""
RGB Additive Color Mixing Diagram Generator

Creates a diagram showing three overlapping circles representing
the primary colors (Red, Green, Blue) and their combinations
(Cyan, Magenta, Yellow, White).

Author: Generated with Claude - Opus 4.5
"""

import numpy as np
from PIL import Image, ImageDraw

def create_rgb_additive_mixing_diagram(size=600):
    """
    Generate an RGB additive color mixing diagram.

    Parameters:
        size: Image size in pixels (square)

    Returns:
        PIL Image object
    """
    # Create a black background (darkness before adding light)
    image = Image.new('RGB', (size, size), (0, 0, 0))

    # Calculate circle positions - equilateral triangle arrangement
    center_x, center_y = size // 2, size // 2
    radius = size // 4
    offset = size // 6  # Distance from center to circle centers

    # Circle centers arranged in equilateral triangle
    # Red at top, Green at bottom-left, Blue at bottom-right
    red_center = (center_x, center_y - offset)
    green_center = (center_x - int(offset * 0.866), center_y + int(offset * 0.5))
    blue_center = (center_x + int(offset * 0.866), center_y + int(offset * 0.5))

    # Create arrays for pixel-by-pixel color calculation
    # This allows proper additive mixing at intersections
    result = np.zeros((size, size, 3), dtype=np.uint8)

    # Create coordinate grids
    y_coords, x_coords = np.ogrid[:size, :size]

    # Calculate distance from each circle center
    dist_red = np.sqrt((x_coords - red_center[0])**2 + (y_coords - red_center[1])**2)
    dist_green = np.sqrt((x_coords - green_center[0])**2 + (y_coords - green_center[1])**2)
    dist_blue = np.sqrt((x_coords - blue_center[0])**2 + (y_coords - blue_center[1])**2)

    # Create masks for each circle
    red_mask = dist_red <= radius
    green_mask = dist_green <= radius
    blue_mask = dist_blue <= radius

    # Apply additive color mixing
    # Where circles overlap, colors add together
    result[:, :, 0] = red_mask * 255      # Red channel
    result[:, :, 1] = green_mask * 255    # Green channel
    result[:, :, 2] = blue_mask * 255     # Blue channel

    # Convert back to PIL Image
    image = Image.fromarray(result, mode='RGB')

    # Add labels using PIL ImageDraw
    draw = ImageDraw.Draw(image)

    # Label positions (outside the circles)
    # Cyan = Green + Blue (bottom center), Magenta = Red + Blue (right), Yellow = Red + Green (left)
    labels = [
        ("Red", red_center[0] - 20, red_center[1] - radius - 30, (255, 100, 100)),
        ("Green", green_center[0] - 50, green_center[1] + radius + 10, (100, 255, 100)),
        ("Blue", blue_center[0] + 10, blue_center[1] + radius + 10, (100, 100, 255)),
        ("Cyan", (green_center[0] + blue_center[0]) // 2 - 20, green_center[1] + 30, (0, 255, 255)),
        ("Magenta", (red_center[0] + blue_center[0]) // 2 + 40, (red_center[1] + blue_center[1]) // 2, (255, 0, 255)),
        ("Yellow", (red_center[0] + green_center[0]) // 2 - 60, (red_center[1] + green_center[1]) // 2, (255, 255, 0)),
        ("White", center_x - 25, center_y - 8, (255, 255, 255))
    ]

    # Draw labels with contrasting outline for readability
    for label, x, y, color in labels:
        # Draw outline (black shadow)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), label, fill=(0, 0, 0))
        # Draw main text
        draw.text((x, y), label, fill=color)

    return image


if __name__ == '__main__':
    # Generate the diagram
    diagram = create_rgb_additive_mixing_diagram(size=600)

    # Save to the images directory
    output_path = '../../../../../images/rgb_additive_mixing.png'
    diagram.save(output_path)
    print(f"RGB additive mixing diagram saved to {output_path}")

    # Also save a local copy for reference
    diagram.save('rgb_additive_mixing_local.png')
    print("Local copy saved to rgb_additive_mixing_local.png")
