import random
import numpy as np
from PIL import Image
import imageio.v2 as imageio

# =============================================================================
# Configuration Parameters
# =============================================================================
WIDTH, HEIGHT = 600, 400          # Canvas dimensions in pixels
GRAIN_SIZE = 3                    # Size of each sand grain in pixels
NUM_FRAMES = 120                  # Total frames in the animation

# Color definitions (RGB format)
BACKGROUND_COLOR = (20, 15, 10)   # Dark brown background
SAND_WAITING = (50, 40, 30)       # Dark color for stationary grains
SAND_BASE = (194, 178, 128)       # Base beige color for moving grains

# =============================================================================
# Sand Grain Class
# =============================================================================
class SandGrain:
    """
    Represents a single grain of sand with position, velocity, and state.

    Each grain waits for a random delay before moving, then accelerates
    rightward to simulate being blown by wind.
    """

    def __init__(self, x, y, target_x):
        # Position (using floats for smooth sub-pixel movement)
        self.x = float(x)
        self.y = float(y)
        self.target_x = target_x

        # Delay before movement starts (Gaussian distribution creates natural variation)
        self.delay = max(0, int(random.gauss(50, 15)))

        # Movement state
        self.is_moving = False
        self.is_finished = False

        # Velocity components
        self.velocity_x = random.uniform(-1.5, 1.5)  # Initial horizontal speed
        self.velocity_y = random.uniform(-0.3, 0.3)  # Slight vertical drift
        self.acceleration = 1.08                      # Speed multiplier per frame

        # Create slightly varied color for natural appearance
        self.color = (
            SAND_BASE[0] + random.randint(-30, 30),
            SAND_BASE[1] + random.randint(-30, 30),
            SAND_BASE[2] + random.randint(-20, 20)
        )

    def update(self):
        """Update grain position and state for one frame."""
        if self.is_finished:
            return

        # Count down delay before moving
        if self.delay > 0:
            self.delay -= 1
            return

        # Mark as moving and update position
        self.is_moving = True
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Accelerate rightward (simulates wind pushing the grain)
        if self.velocity_x < 1.0:
            self.velocity_x += 0.2  # Redirect leftward motion to right
        else:
            self.velocity_x *= self.acceleration

        # Check if grain has left the canvas
        if self.x >= self.target_x or self.y < 0 or self.y >= HEIGHT:
            self.is_finished = True

# =============================================================================
# Simulation Functions
# =============================================================================
def create_sand_grains(start_x, end_x, start_y, end_y):
    """Create a grid of sand grains covering a rectangular region."""
    grains = []
    for x in range(start_x, end_x, GRAIN_SIZE):
        for y in range(start_y, end_y, GRAIN_SIZE):
            grains.append(SandGrain(x, y, WIDTH - 2))
    return grains

def draw_grains(frame, grains):
    """Draw all grains onto the frame array."""
    for grain in grains:
        if grain.is_finished:
            continue

        # Choose color based on movement state
        color = grain.color if grain.is_moving else SAND_WAITING

        # Draw grain as a small square
        x, y = int(grain.x), int(grain.y)
        if 0 <= x < WIDTH - GRAIN_SIZE and 0 <= y < HEIGHT - GRAIN_SIZE:
            frame[y:y + GRAIN_SIZE, x:x + GRAIN_SIZE] = color

def run_simulation():
    """Run the complete sand simulation and save outputs."""
    # Create sand grains in the center of the canvas
    grains = create_sand_grains(150, 450, 100, 300)
    print(f"Created {len(grains)} sand grains")

    frames = []

    for frame_num in range(NUM_FRAMES):
        # Create blank frame with background color
        frame = np.full((HEIGHT, WIDTH, 3), BACKGROUND_COLOR, dtype=np.uint8)

        # Update all grains
        for grain in grains:
            grain.update()

        # Draw all grains
        draw_grains(frame, grains)
        frames.append(frame)

        # Progress indicator
        if frame_num % 30 == 0:
            active = sum(1 for g in grains if not g.is_finished)
            print(f"Frame {frame_num}/{NUM_FRAMES}, Active grains: {active}")

    # Save animated GIF
    imageio.mimsave('sand_animation.gif', frames, fps=24, loop=0)
    print("Saved: sand_animation.gif")

    # Save a snapshot from midway through the animation
    snapshot_frame = frames[NUM_FRAMES // 3]
    Image.fromarray(snapshot_frame).save('sand_snapshot.png')
    print("Saved: sand_snapshot.png")

# =============================================================================
# Main Entry Point
# =============================================================================
if __name__ == '__main__':
    run_simulation()
