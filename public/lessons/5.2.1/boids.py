import numpy as np
from PIL import Image, ImageDraw
import imageio
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Configuration Parameters
# =============================================================================

# Canvas settings
WIDTH = 512
HEIGHT = 512
BACKGROUND_COLOR = (20, 20, 30)  # Dark blue-gray

# Boid settings
NUM_BOIDS = 50
BOID_COLOR = (0, 200, 200)  # Cyan/teal
BOID_SIZE = 8  # Size of triangle

# Behavior parameters (adjust these in Exercise 2)
SEPARATION_WEIGHT = 1.5  # Strength of separation force
ALIGNMENT_WEIGHT = 1.0   # Strength of alignment force
COHESION_WEIGHT = 1.0    # Strength of cohesion force
PERCEPTION_RADIUS = 50   # How far boids can see neighbors
MAX_SPEED = 4            # Maximum velocity magnitude
MAX_FORCE = 0.3          # Maximum steering force

# Animation settings
NUM_FRAMES = 180
FPS = 30

# =============================================================================
# Boid Simulation Functions
# =============================================================================

def initialize_boids(num_boids):
    """
    Create boids with random positions and velocities.

    Returns:
        positions: Array of shape (num_boids, 2) with x, y coordinates
        velocities: Array of shape (num_boids, 2) with vx, vy components
    """
    # Random positions across the canvas
    positions = np.random.rand(num_boids, 2) * np.array([WIDTH, HEIGHT])

    # Random velocities with small initial speed
    angles = np.random.rand(num_boids) * 2 * np.pi
    speeds = np.random.rand(num_boids) * 2 + 1
    velocities = np.column_stack([np.cos(angles) * speeds, np.sin(angles) * speeds])

    return positions, velocities

def compute_distances(positions):
    """
    Compute pairwise distances between all boids.

    Returns:
        distances: Matrix of shape (num_boids, num_boids) with distances
        differences: Array of shape (num_boids, num_boids, 2) with position differences
    """
    # Compute differences accounting for toroidal wrapping
    differences = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]

    # Handle wrapping (shortest distance on torus)
    differences[:, :, 0] = np.where(
        np.abs(differences[:, :, 0]) > WIDTH / 2,
        differences[:, :, 0] - np.sign(differences[:, :, 0]) * WIDTH,
        differences[:, :, 0]
    )
    differences[:, :, 1] = np.where(
        np.abs(differences[:, :, 1]) > HEIGHT / 2,
        differences[:, :, 1] - np.sign(differences[:, :, 1]) * HEIGHT,
        differences[:, :, 1]
    )

    distances = np.sqrt(np.sum(differences ** 2, axis=2))
    return distances, differences

def separation(positions, velocities, distances, differences):
    """
    Rule 1: Steer away from nearby boids to avoid crowding.

    Each boid steers away from boids that are too close.
    """
    steering = np.zeros_like(positions)

    for i in range(len(positions)):
        # Find boids that are too close (within half perception radius)
        close_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS / 2)

        if np.any(close_mask):
            # Steer away from close neighbors (inverse of their direction)
            away_vectors = -differences[i, close_mask]
            # Weight by inverse distance (closer = stronger push)
            weights = 1 / (distances[i, close_mask] + 0.1)
            steering[i] = np.sum(away_vectors * weights[:, np.newaxis], axis=0)

    return steering

def alignment(positions, velocities, distances):
    """
    Rule 2: Match velocity with nearby boids.

    Each boid tries to match the average heading of its neighbors.
    """
    steering = np.zeros_like(positions)

    for i in range(len(positions)):
        # Find neighbors within perception radius
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)

        if np.any(neighbor_mask):
            # Average velocity of neighbors
            average_velocity = np.mean(velocities[neighbor_mask], axis=0)
            # Steer toward average velocity
            steering[i] = average_velocity - velocities[i]

    return steering

def cohesion(positions, velocities, distances, differences):
    """
    Rule 3: Move toward the center of nearby boids.

    Each boid steers toward the average position of its neighbors.
    """
    steering = np.zeros_like(positions)

    for i in range(len(positions)):
        # Find neighbors within perception radius
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)

        if np.any(neighbor_mask):
            # Average position of neighbors (relative to current boid)
            center_offset = -np.mean(differences[i, neighbor_mask], axis=0)
            # Steer toward center
            steering[i] = center_offset

    return steering

def limit_magnitude(vectors, max_magnitude):
    """Limit the magnitude of vectors to a maximum value."""
    magnitudes = np.sqrt(np.sum(vectors ** 2, axis=1, keepdims=True))
    magnitudes = np.maximum(magnitudes, 0.0001)  # Avoid division by zero
    scale = np.minimum(1.0, max_magnitude / magnitudes)
    return vectors * scale

def update_boids(positions, velocities):
    """
    Update all boids for one time step.

    Applies all three rules and updates positions/velocities.
    """
    # Compute distances between all boids
    distances, differences = compute_distances(positions)

    # Calculate forces from each rule
    separation_force = separation(positions, velocities, distances, differences)
    alignment_force = alignment(positions, velocities, distances)
    cohesion_force = cohesion(positions, velocities, distances, differences)

    # Combine forces with weights
    acceleration = (
        separation_force * SEPARATION_WEIGHT +
        alignment_force * ALIGNMENT_WEIGHT +
        cohesion_force * COHESION_WEIGHT
    )

    # Limit steering force
    acceleration = limit_magnitude(acceleration, MAX_FORCE)

    # Update velocity
    velocities = velocities + acceleration
    velocities = limit_magnitude(velocities, MAX_SPEED)

    # Update position
    positions = positions + velocities

    # Wrap around edges (toroidal boundary)
    positions[:, 0] = positions[:, 0] % WIDTH
    positions[:, 1] = positions[:, 1] % HEIGHT

    return positions, velocities

# =============================================================================
# Rendering Functions
# =============================================================================

def draw_triangle(draw, x, y, angle, size, color):
    """
    Draw a triangle pointing in the given direction.

    The triangle represents a boid, with the point indicating heading.
    """
    # Triangle vertices relative to center
    # Point at front, two points at back
    front = (x + np.cos(angle) * size, y + np.sin(angle) * size)
    back_left = (
        x + np.cos(angle + 2.5) * size * 0.6,
        y + np.sin(angle + 2.5) * size * 0.6
    )
    back_right = (
        x + np.cos(angle - 2.5) * size * 0.6,
        y + np.sin(angle - 2.5) * size * 0.6
    )

    draw.polygon([front, back_left, back_right], fill=color)

def render_frame(positions, velocities):
    """
    Render one frame of the simulation.

    Returns:
        frame: NumPy array of shape (HEIGHT, WIDTH, 3)
    """
    # Create image with background color
    image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    # Draw each boid as a triangle pointing in velocity direction
    for i in range(len(positions)):
        x, y = positions[i]
        vx, vy = velocities[i]

        # Calculate angle from velocity
        angle = np.arctan2(vy, vx)

        draw_triangle(draw, x, y, angle, BOID_SIZE, BOID_COLOR)

    return np.array(image)

# =============================================================================
# Main Simulation
# =============================================================================

def run_simulation():
    """
    Run the boids simulation and save output.

    Generates:
        - boids_simulation.gif: Animated simulation
        - boids_frame.png: Single frame for documentation
    """
    print("Initializing boids simulation...")
    positions, velocities = initialize_boids(NUM_BOIDS)

    frames = []

    # Save animation

    gif_path = os.path.join(SCRIPT_DIR, 'boids_simulation.gif')
    imageio.mimsave(gif_path, frames, fps=FPS, loop=0)
    print("Saved boids_simulation.gif")

    print("Simulation complete!")

if __name__ == '__main__':
    run_simulation()
