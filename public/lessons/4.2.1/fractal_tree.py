import math
from PIL import Image, ImageDraw

def draw_branch(draw, x, y, length, angle, depth, branch_angle, length_ratio):
    """
    Recursively draw a fractal tree branch.

    Parameters:
        draw: PIL ImageDraw object
        x, y: Starting coordinates of the branch
        length: Length of this branch in pixels
        angle: Direction of growth in radians (0 = right, pi/2 = up)
        depth: Remaining recursion depth (0 = stop)
        branch_angle: Angle between child branches and parent (radians)
        length_ratio: Child branch length as fraction of parent
    """
    if depth == 0:
        return

    # Calculate the endpoint using polar to Cartesian conversion
    end_x = x + length * math.sin(angle)
    end_y = y - length * math.cos(angle)  # Subtract because y increases downward

    # Draw the branch with thickness based on depth
    thickness = max(1, depth // 2)
    brown = (101, 67, 33)  # Natural wood color
    draw.line([(x, y), (end_x, end_y)], fill=brown, width=thickness)

    # Calculate the new length for child branches
    new_length = length * length_ratio

    # Recursively draw the left and right child branches
    draw_branch(draw, end_x, end_y, new_length, angle - branch_angle,
                depth - 1, branch_angle, length_ratio)
    draw_branch(draw, end_x, end_y, new_length, angle + branch_angle,
                depth - 1, branch_angle, length_ratio)

def create_fractal_tree(width=512, height=512, depth=8, branch_angle_degrees=25,
                        length_ratio=0.7, trunk_length=120):
    """
    Create a fractal tree image.

    Parameters:
        width, height: Image dimensions in pixels
        depth: Maximum recursion depth (number of branching levels)
        branch_angle_degrees: Angle between branches in degrees
        length_ratio: How much smaller each child branch is (0.5 to 0.85)
        trunk_length: Initial trunk length in pixels

    Returns:
        PIL Image object
    """
    # Create a white background image
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Convert branch angle from degrees to radians
    branch_angle = math.radians(branch_angle_degrees)

    # Start the tree from the bottom center of the image
    start_x = width // 2
    start_y = height - 50  # Leave some margin at the bottom
    start_angle = 0  # Initial direction: straight up (0 radians from vertical)

    # Draw the tree recursively
    draw_branch(draw, start_x, start_y, trunk_length, start_angle,
                depth, branch_angle, length_ratio)

    return image

# Main execution
if __name__ == '__main__':
    # Create a fractal tree with default parameters
    tree_image = create_fractal_tree(
        width=512,
        height=512,
        depth=8,
        branch_angle_degrees=25,
        length_ratio=0.7,
        trunk_length=120
    )

    # Save the result
    tree_image.save('fractal_tree_basic.png')
    print("Fractal tree saved to fractal_tree_basic.png")
