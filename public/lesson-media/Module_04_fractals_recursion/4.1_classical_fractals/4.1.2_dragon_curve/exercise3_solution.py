import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio.v2 as imageio

# Direction constants
LEFT, UP, RIGHT, DOWN = range(4)

def turn_left(direction):
    """Rotate 90 degrees counter-clockwise."""
    return (direction + 3) % 4

def turn_right(direction):
    """Rotate 90 degrees clockwise."""
    return (direction + 1) % 4

def invert_sequence(sequence):
    """Swap all L's and R's in the sequence."""
    return ''.join(['L' if char == 'R' else 'R' for char in sequence])

def generate_dragon_sequence(initial_turn, depth):
    """Generate the dragon curve turn sequence recursively."""
    if depth == 0:
        return initial_turn
    else:
        previous = generate_dragon_sequence(initial_turn, depth - 1)
        second_half = invert_sequence(previous[::-1])
        return previous + 'R' + second_half

def draw_partial_dragon(sequence, num_segments, canvas_size=300):
    """Draw the dragon curve up to a specific number of segments."""
    canvas = np.zeros((canvas_size, canvas_size, 3), dtype=np.uint8)
    canvas[:] = 20  # Dark background

    step_size = 15
    start_x = int(canvas_size * 0.55)
    start_y = int(canvas_size * 0.35)

    position = (start_x, start_y)
    direction = UP
    color = (100, 180, 255)

    # Draw segments up to num_segments
    segments_drawn = 0

    for i, turn in enumerate(sequence):
        if segments_drawn >= num_segments:
            break

        x, y = position

        # Draw line segment
        if direction == RIGHT:
            end_x = min(x + step_size, canvas_size - 1)
            if 0 <= y < canvas_size:
                canvas[y, x:end_x] = color
            position = (end_x, y)
        elif direction == LEFT:
            start_x_pos = max(x - step_size, 0)
            if 0 <= y < canvas_size:
                canvas[y, start_x_pos:x] = color
            position = (start_x_pos, y)
        elif direction == UP:
            start_y_pos = max(y - step_size, 0)
            if 0 <= x < canvas_size:
                canvas[start_y_pos:y, x] = color
            position = (x, start_y_pos)
        elif direction == DOWN:
            end_y = min(y + step_size, canvas_size - 1)
            if 0 <= x < canvas_size:
                canvas[y:end_y, x] = color
            position = (x, end_y)

        segments_drawn += 1

        # Turn
        if turn == 'R':
            direction = turn_right(direction)
        else:
            direction = turn_left(direction)

    # Draw final segment if we haven't reached the limit
    if segments_drawn < num_segments:
        x, y = position
        if direction == RIGHT:
            end_x = min(x + step_size, canvas_size - 1)
            if 0 <= y < canvas_size:
                canvas[y, x:end_x] = color
        elif direction == LEFT:
            start_x_pos = max(x - step_size, 0)
            if 0 <= y < canvas_size:
                canvas[y, start_x_pos:x] = color
        elif direction == UP:
            start_y_pos = max(y - step_size, 0)
            if 0 <= x < canvas_size:
                canvas[start_y_pos:y, x] = color
        elif direction == DOWN:
            end_y = min(y + step_size, canvas_size - 1)
            if 0 <= x < canvas_size:
                canvas[y:end_y, x] = color

    return canvas

def add_label(image_array, text):
    """Add a text label to the frame."""
    image = Image.fromarray(image_array)
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    # Draw text with shadow
    draw.text((11, 11), text, fill=(50, 50, 50), font=font)
    draw.text((10, 10), text, fill=(255, 255, 255), font=font)

    return np.array(image)

if __name__ == "__main__":
    # Generate depth 3 dragon curve (the test case)
    depth = 3
    sequence = generate_dragon_sequence('R', depth)
    total_segments = len(sequence) + 1  # Number of line segments

    print(f"Depth {depth} sequence: {sequence}")
    print(f"Total segments: {total_segments}")

    frames = []
    canvas_size = 300

    # Create animation frames showing the curve being drawn
    for i in range(1, total_segments + 1):
        frame = draw_partial_dragon(sequence, i, canvas_size)
        frame = add_label(frame, f"Depth 3: Segment {i}/{total_segments}")
        frames.append(frame)

        # Add extra copies for pacing (slower at key moments)
        if i == total_segments:
            # Hold final frame longer
            for _ in range(5):
                frames.append(frame)

    # Save as animated GIF
    imageio.mimsave(
        'exercise3_expected_output.gif',
        frames,
        fps=4,
        loop=0
    )

    print(f"Saved exercise3_expected_output.gif ({len(frames)} frames)")
