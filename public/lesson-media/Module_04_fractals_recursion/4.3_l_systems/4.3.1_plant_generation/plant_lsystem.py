import numpy as np
from PIL import Image, ImageDraw
import math

# =============================================================================
# L-System Configuration
# =============================================================================

# Starting symbol for the L-System
AXIOM = "F"

# Production rules: each symbol maps to a replacement string
# F -> F[+F]F[-F]F creates a branching plant structure
RULES = {"F": "F[+F]F[-F]F"}

# Number of times to apply the production rules
ITERATIONS = 4

# Angle to turn when encountering + or - symbols (in degrees)
ANGLE = 25.7

# =============================================================================
# Image Settings
# =============================================================================

WIDTH = 800
HEIGHT = 600
BACKGROUND_COLOR = (10, 20, 30)      # Dark blue-gray background
LINE_COLOR = (100, 180, 100)         # Green color for plant stems
LINE_WIDTH = 1

# =============================================================================
# L-System Functions
# =============================================================================

def apply_rules(axiom, rules, iterations):
    """
    Apply production rules to the axiom string for a given number of iterations.

    Each iteration replaces every character in the string according to the rules.
    Characters without rules remain unchanged.

    Parameters:
        axiom: Starting string (e.g., "F")
        rules: Dictionary mapping characters to replacement strings
        iterations: Number of times to apply the rules

    Returns:
        Final string after all iterations
    """
    current_string = axiom

    for iteration in range(iterations):
        next_string = ""

        # Process each character in the current string
        for character in current_string:
            # Apply rule if it exists, otherwise keep the character
            replacement = rules.get(character, character)
            next_string += replacement

        current_string = next_string

    return current_string

def draw_lsystem(instructions, angle_degrees, step_size, image_width, image_height):
    """
    Convert an L-System instruction string into an image using turtle graphics.

    Symbol meanings:
        F = Move forward and draw a line
        + = Turn left by angle
        - = Turn right by angle
        [ = Save current position and angle (push to stack)
        ] = Restore saved position and angle (pop from stack)

    Parameters:
        instructions: L-System string to interpret
        angle_degrees: Angle to turn for + and - commands
        step_size: Length of each forward movement
        image_width: Width of the output image
        image_height: Height of the output image

    Returns:
        PIL Image with the rendered L-System
    """
    # Create a blank image
    image = Image.new("RGB", (image_width, image_height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    # Convert angle to radians for math functions
    angle_radians = math.radians(angle_degrees)

    # Starting position (bottom center of image, pointing up)
    x = image_width // 2
    y = image_height - 50
    current_angle = -math.pi / 2  # Point upward (negative y direction)

    # Stack for saving and restoring turtle state
    state_stack = []

    # Process each instruction character
    for symbol in instructions:

        if symbol == "F":
            # Move forward and draw a line
            new_x = x + step_size * math.cos(current_angle)
            new_y = y + step_size * math.sin(current_angle)
            draw.line([(x, y), (new_x, new_y)], fill=LINE_COLOR, width=LINE_WIDTH)
            x, y = new_x, new_y

        elif symbol == "+":
            # Turn left (counterclockwise)
            current_angle -= angle_radians

        elif symbol == "-":
            # Turn right (clockwise)
            current_angle += angle_radians

        elif symbol == "[":
            # Save current state to stack
            state_stack.append((x, y, current_angle))

        elif symbol == "]":
            # Restore state from stack
            if state_stack:
                x, y, current_angle = state_stack.pop()

    return image

def generate_plant(iterations=ITERATIONS, angle=ANGLE, step_size=5):
    """
    Generate a complete plant image with the default L-System configuration.

    Parameters:
        iterations: Number of rule applications (affects complexity)
        angle: Branching angle in degrees
        step_size: Length of each line segment

    Returns:
        PIL Image of the generated plant
    """
    # Generate the instruction string
    instructions = apply_rules(AXIOM, RULES, iterations)

    # Render the instructions as an image
    plant_image = draw_lsystem(instructions, angle, step_size, WIDTH, HEIGHT)

    return plant_image

# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    # Generate the plant image
    plant_image = generate_plant(iterations=4, angle=25.7, step_size=5)

    # Save the result
    plant_image.save("plant_basic.png")

    # Print information about the generation
    instructions = apply_rules(AXIOM, RULES, 4)
    print(f"Plant generated successfully!")
    print(f"  Axiom: {AXIOM}")
    print(f"  Rule: F -> {RULES['F']}")
    print(f"  Iterations: 4")
    print(f"  Instruction length: {len(instructions)} characters")
    print(f"  Saved to: plant_basic.png")
