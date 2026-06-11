import numpy as np
from PIL import Image

# =============================================================================
# Direction Constants
# =============================================================================
# We use integers 0-3 to represent the four cardinal directions.
# This makes rotation simple: add 1 for clockwise, add 3 for counter-clockwise.
LEFT, UP, RIGHT, DOWN = range(4)

def turn_left(direction):
    """
    Rotate the current direction 90 degrees counter-clockwise.

    Parameters:
        direction: Current direction (0=LEFT, 1=UP, 2=RIGHT, 3=DOWN)

    Returns:
        New direction after turning left
    """
    return (direction + 3) % 4

def turn_right(direction):
    """
    Rotate the current direction 90 degrees clockwise.

    Parameters:
        direction: Current direction (0=LEFT, 1=UP, 2=RIGHT, 3=DOWN)

    Returns:
        New direction after turning right
    """
    return (direction + 1) % 4

def move_forward(canvas, position, step_size, direction, color):
    """
    Draw a line segment in the current direction on the canvas.

    Parameters:
        canvas: NumPy array representing the image
        position: Tuple (x, y) of current position
        step_size: Length of the line segment in pixels
        direction: Current direction (0=LEFT, 1=UP, 2=RIGHT, 3=DOWN)
        color: Tuple (R, G, B) for the line color

    Returns:
        New position after moving forward
    """
    x, y = position

    if direction == RIGHT:
        # Draw horizontal line to the right
        canvas[y, x:x + step_size] = color
        return (x + step_size, y)

    elif direction == LEFT:
        # Draw horizontal line to the left
        canvas[y, x - step_size:x] = color
        return (x - step_size, y)

    elif direction == UP:
        # Draw vertical line upward (y decreases)
        canvas[y - step_size:y, x] = color
        return (x, y - step_size)

    elif direction == DOWN:
        # Draw vertical line downward (y increases)
        canvas[y:y + step_size, x] = color
        return (x, y + step_size)

# =============================================================================
# Dragon Curve Sequence Generation
# =============================================================================

def invert_sequence(sequence):
    """
    Invert a sequence by swapping all L's and R's.

    This is part of the dragon curve construction rule:
    When we "unfold" the paper, the second half is the inverted reverse
    of the first half.

    Parameters:
        sequence: String of 'L' and 'R' characters

    Returns:
        Inverted sequence with L<->R swapped
    """
    return ''.join(['L' if char == 'R' else 'R' for char in sequence])

def generate_dragon_sequence(initial_turn, depth):
    """
    Generate the dragon curve sequence recursively.

    The construction rule is:
        dragon(0) = initial_turn (usually 'R')
        dragon(n) = dragon(n-1) + 'R' + reverse(invert(dragon(n-1)))

    This mimics folding a strip of paper n times, then unfolding it
    so each fold opens to 90 degrees.

    Parameters:
        initial_turn: Starting sequence (usually 'R')
        depth: Number of recursive iterations (folds)

    Returns:
        String of 'L' and 'R' characters representing the turn sequence
    """
    if depth == 0:
        return initial_turn
    else:
        # Get the sequence from the previous depth
        previous = generate_dragon_sequence(initial_turn, depth - 1)

        # The second half is the reversed, inverted previous sequence
        second_half = invert_sequence(previous[::-1])

        # Combine: previous + R (the fold point) + second_half
        return previous + 'R' + second_half

def draw_dragon_curve(canvas, sequence, start_position, step_size,
                      start_direction, color):
    """
    Render the dragon curve on a canvas using turtle graphics.

    The sequence is interpreted as:
    - Move forward one step
    - Turn according to the character ('L' = left, 'R' = right)
    - Repeat for each character
    - Move forward one final step

    Parameters:
        canvas: NumPy array to draw on
        sequence: String of 'L' and 'R' turn instructions
        start_position: Tuple (x, y) starting coordinates
        step_size: Pixel length of each forward movement
        start_direction: Initial direction (UP, DOWN, LEFT, RIGHT)
        color: RGB tuple for the line color
    """
    position = start_position
    direction = start_direction

    # Draw each segment, turning after each one
    for turn in sequence:
        position = move_forward(canvas, position, step_size, direction, color)

        if turn == 'R':
            direction = turn_right(direction)
        else:
            direction = turn_left(direction)

    # Draw the final segment
    position = move_forward(canvas, position, step_size, direction, color)

# =============================================================================
# Main Script
# =============================================================================

if __name__ == "__main__":
    # Canvas dimensions (slightly rectangular to fit the dragon shape)
    height, width = 600, 800

    # Create a black canvas
    canvas = np.zeros((height, width, 3), dtype=np.uint8)

    # Dragon curve parameters
    depth = 10                    # Number of recursive iterations (folds)
    step_size = 3                 # Pixel size of each line segment
    start_position = (550, 180)   # Starting (x, y) position - tuned for this depth
    start_direction = UP          # Initial direction to face

    # Color: light blue (a classic dragon curve color)
    dragon_color = (100, 180, 255)

    # Generate the turn sequence
    sequence = generate_dragon_sequence('R', depth)
    print(f"Dragon curve depth {depth}: {len(sequence)} turns")
    print(f"Sequence preview: {sequence[:50]}...")

    # Draw the dragon curve
    draw_dragon_curve(canvas, sequence, start_position, step_size,
                      start_direction, dragon_color)

    # Save the image
    image = Image.fromarray(canvas)
    image.save('dragon_curve.png')
    print("Image saved as dragon_curve.png")
