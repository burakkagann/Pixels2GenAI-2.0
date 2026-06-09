import math
from PIL import Image, ImageDraw

def draw_branch(draw, x, y, length, angle, depth, branch_angle, length_ratio):
    """
    Recursively draw a fractal tree branch.

    Parameters:
        draw: PIL ImageDraw object for drawing lines
        x, y: Starting coordinates of this branch
        length: Length of this branch in pixels
        angle: Direction of growth in radians (0 = straight up)
        depth: Remaining recursion depth (stop when 0)
        branch_angle: Angle offset for child branches (radians)
        length_ratio: How much smaller child branches are (0.0 to 1.0)

    TODO: Implement this function following these steps:
    1. Check the base case: if depth is 0, return immediately
    2. Calculate the endpoint using trigonometry:
       - end_x = x + length * sin(angle)
       - end_y = y - length * cos(angle)  (subtract because y increases downward)
    3. Draw a line from (x, y) to (end_x, end_y)
    4. Calculate the new length for child branches
    5. Recursively call draw_branch for the left branch (angle - branch_angle)
    6. Recursively call draw_branch for the right branch (angle + branch_angle)
    """
    # Your code here
    pass

def create_fractal_tree():
    """Create and save a fractal tree image."""
    # Image settings
    width, height = 512, 512

    # Tree parameters
    depth = 8                           # Number of branching levels
    branch_angle = math.radians(25)     # Angle between branches (25 degrees)
    length_ratio = 0.7                  # Child branches are 70% of parent
    trunk_length = 120                  # Starting trunk length in pixels

    # Create the image with white background
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)

    # Starting position: bottom center of image
    start_x = width // 2
    start_y = height - 50

    # Draw the tree
    draw_branch(draw, start_x, start_y, trunk_length, 0,
                depth, branch_angle, length_ratio)

    # Save the result
    image.save('my_fractal_tree.png')
    print("Tree saved to my_fractal_tree.png")

if __name__ == '__main__':
    create_fractal_tree()
