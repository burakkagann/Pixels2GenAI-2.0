import random
import numpy as np
from PIL import Image
import imageio.v2 as imageio

# =============================================================================
# Configuration
# =============================================================================
WIDTH, HEIGHT = 400, 300
NUM_FRAMES = 60
BACKGROUND_COLOR = (10, 10, 20)  # Dark blue-gray background

# =============================================================================
# Particle Class
# =============================================================================
class Particle:
    """A single particle with position, velocity, and color."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.is_active = True

        # TODO 1: Initialize velocity_x and velocity_y
        # For rain: mostly downward (y positive), slight horizontal drift
        # For bubbles: mostly upward (y negative), slight horizontal wiggle
        # For confetti: random direction outward from center
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        # TODO 2: Set the particle color (RGB tuple)
        # For rain: light blue shades (150-200, 200-255, 255)
        # For bubbles: light cyan (100-150, 200-255, 255)
        # For confetti: random bright colors
        self.color = (255, 255, 255)

    def update(self):
        """Update particle position each frame."""
        if not self.is_active:
            return

        # TODO 3: Update position using velocity
        # self.x += self.velocity_x
        # self.y += self.velocity_y

        # TODO 4: Add any special physics effects
        # For rain: maybe add slight acceleration (gravity)
        # For bubbles: add oscillating motion (wiggle)
        # For confetti: add friction (slow down over time)

        # TODO 5: Check bounds and deactivate if off-screen
        # if self.y > HEIGHT or self.y < 0 or self.x < 0 or self.x > WIDTH:
        #     self.is_active = False
        pass

# =============================================================================
# Helper Functions
# =============================================================================
def create_particles(count, spawn_mode='center'):
    """
    Create particles based on spawn mode.

    spawn_mode options:
        'top'    - Spawn along top edge (for rain)
        'bottom' - Spawn along bottom edge (for bubbles)
        'center' - Spawn at center point (for confetti burst)
    """
    particles = []

    # TODO 6: Create particles based on spawn_mode
    # for i in range(count):
    #     if spawn_mode == 'top':
    #         x = random.randint(0, WIDTH)
    #         y = 0
    #     elif spawn_mode == 'bottom':
    #         x = random.randint(0, WIDTH)
    #         y = HEIGHT
    #     else:  # center
    #         x = WIDTH // 2
    #         y = HEIGHT // 2
    #     particles.append(Particle(x, y))

    return particles

def draw_particles(frame, particles):
    """Draw all active particles onto the frame."""
    for p in particles:
        if not p.is_active:
            continue
        x, y = int(p.x), int(p.y)
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            # Draw a small 2x2 pixel square for each particle
            frame[y:min(y+2, HEIGHT), x:min(x+2, WIDTH)] = p.color

# =============================================================================
# Main Simulation
# =============================================================================
def run_simulation():
    """Run the particle simulation and save the animation."""
    # TODO 7: Adjust particle count and spawn mode for your effect
    # Rain: 100-200 particles, spawn_mode='top'
    # Bubbles: 50-100 particles, spawn_mode='bottom'
    # Confetti: 200-300 particles, spawn_mode='center'
    particles = create_particles(100, spawn_mode='center')

    frames = []

    for frame_num in range(NUM_FRAMES):
        # Create blank frame
        frame = np.full((HEIGHT, WIDTH, 3), BACKGROUND_COLOR, dtype=np.uint8)

        # Update all particles
        for p in particles:
            p.update()

        # Draw all particles
        draw_particles(frame, particles)
        frames.append(frame)

    # Save animation
    imageio.mimsave('my_particle_effect.gif', frames, fps=30, loop=0)
    print("Saved: my_particle_effect.gif")

if __name__ == '__main__':
    run_simulation()
