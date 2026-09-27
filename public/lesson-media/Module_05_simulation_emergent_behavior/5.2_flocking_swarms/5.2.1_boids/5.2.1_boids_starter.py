import numpy as np
from PIL import Image, ImageDraw
import imageio
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Configuration
# =============================================================================

WIDTH = 512
HEIGHT = 512
BACKGROUND_COLOR = (20, 20, 30)

NUM_BOIDS = 50
BOID_COLOR = (0, 200, 200)
BOID_SIZE = 8

SEPARATION_WEIGHT = 1.5
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0
PERCEPTION_RADIUS = 50
MAX_SPEED = 4
MAX_FORCE = 0.3

NUM_FRAMES = 180
FPS = 30

# Obstacle configuration (for Exercise 3)
OBSTACLE_X = WIDTH // 2   # Center of canvas
OBSTACLE_Y = HEIGHT // 2
OBSTACLE_RADIUS = 60      # Size of the obstacle
OBSTACLE_COLOR = (100, 50, 50)  # Dark red

# Weight for obstacle avoidance (adjust to change strength)
OBSTACLE_AVOIDANCE_WEIGHT = 2.0

# =============================================================================
# Boid Functions (provided, do not modify)
# =============================================================================

def initialize_boids(num_boids):
    """Create boids with random positions and velocities."""
    positions = np.random.rand(num_boids, 2) * np.array([WIDTH, HEIGHT])
    angles = np.random.rand(num_boids) * 2 * np.pi
    speeds = np.random.rand(num_boids) * 2 + 1
    velocities = np.column_stack([np.cos(angles) * speeds, np.sin(angles) * speeds])
    return positions, velocities

def compute_distances(positions):
    """Compute pairwise distances between all boids."""
    differences = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
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
    """Rule 1: Steer away from nearby boids."""
    steering = np.zeros_like(positions)
    for i in range(len(positions)):
        close_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS / 2)
        if np.any(close_mask):
            away_vectors = -differences[i, close_mask]
            weights = 1 / (distances[i, close_mask] + 0.1)
            steering[i] = np.sum(away_vectors * weights[:, np.newaxis], axis=0)
    return steering

def alignment(positions, velocities, distances):
    """Rule 2: Match velocity with nearby boids."""
    steering = np.zeros_like(positions)
    for i in range(len(positions)):
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)
        if np.any(neighbor_mask):
            average_velocity = np.mean(velocities[neighbor_mask], axis=0)
            steering[i] = average_velocity - velocities[i]
    return steering

def cohesion(positions, velocities, distances, differences):
    """Rule 3: Move toward the center of nearby boids."""
    steering = np.zeros_like(positions)
    for i in range(len(positions)):
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)
        if np.any(neighbor_mask):
            center_offset = -np.mean(differences[i, neighbor_mask], axis=0)
            steering[i] = center_offset
    return steering

def limit_magnitude(vectors, max_magnitude):
    """Limit the magnitude of vectors to a maximum value."""
    magnitudes = np.sqrt(np.sum(vectors ** 2, axis=1, keepdims=True))
    magnitudes = np.maximum(magnitudes, 0.0001)
    scale = np.minimum(1.0, max_magnitude / magnitudes)
    return vectors * scale

# =============================================================================
# TODO: Implement obstacle avoidance
# =============================================================================

def obstacle_avoidance(positions):
    """
    Rule 4: Steer away from obstacles.

    TODO: Implement this function!

    For each boid:
    1. Calculate the distance from the boid to the obstacle center
    2. If the boid is within OBSTACLE_RADIUS * 1.5, it should steer away
    3. The steering force should point away from the obstacle
    4. Closer boids should experience stronger avoidance force

    Hints:
    - The obstacle is at (OBSTACLE_X, OBSTACLE_Y)
    - Use: direction = position - obstacle_center
    - Normalize and scale by inverse distance for stronger effect when close

    Returns:
        steering: Array of shape (num_boids, 2) with avoidance forces
    """
    steering = np.zeros_like(positions)

    # YOUR CODE HERE
    # -------------------------------------------------------------------------
    # Example structure (uncomment and complete):
    #
    # obstacle_center = np.array([OBSTACLE_X, OBSTACLE_Y])
    #
    # for i in range(len(positions)):
    #     # Calculate vector from obstacle to boid
    #     direction = positions[i] - obstacle_center
    #     distance = np.sqrt(np.sum(direction ** 2))
    #
    #     # Check if boid is within avoidance range
    #     if distance < OBSTACLE_RADIUS * 1.5:
    #         # Calculate avoidance force
    #         # Stronger when closer (inverse distance)
    #         pass  # Replace with your implementation
    #
    # -------------------------------------------------------------------------

    return steering

# =============================================================================
# Update and Render (modified to include obstacle avoidance)
# =============================================================================

def update_boids(positions, velocities):
    """Update all boids including obstacle avoidance."""
    distances, differences = compute_distances(positions)

    separation_force = separation(positions, velocities, distances, differences)
    alignment_force = alignment(positions, velocities, distances)
    cohesion_force = cohesion(positions, velocities, distances, differences)
    obstacle_force = obstacle_avoidance(positions)  # New rule!

    acceleration = (
        separation_force * SEPARATION_WEIGHT +
        alignment_force * ALIGNMENT_WEIGHT +
        cohesion_force * COHESION_WEIGHT +
        obstacle_force * OBSTACLE_AVOIDANCE_WEIGHT  # Add obstacle force
    )

    acceleration = limit_magnitude(acceleration, MAX_FORCE)
    velocities = velocities + acceleration
    velocities = limit_magnitude(velocities, MAX_SPEED)
    positions = positions + velocities
    positions[:, 0] = positions[:, 0] % WIDTH
    positions[:, 1] = positions[:, 1] % HEIGHT

    return positions, velocities

def draw_triangle(draw, x, y, angle, size, color):
    """Draw a triangle representing a boid."""
    front = (x + np.cos(angle) * size, y + np.sin(angle) * size)
    back_left = (x + np.cos(angle + 2.5) * size * 0.6, y + np.sin(angle + 2.5) * size * 0.6)
    back_right = (x + np.cos(angle - 2.5) * size * 0.6, y + np.sin(angle - 2.5) * size * 0.6)
    draw.polygon([front, back_left, back_right], fill=color)

def render_frame(positions, velocities):
    """Render one frame including the obstacle."""
    image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    # Draw obstacle as a circle
    draw.ellipse([
        OBSTACLE_X - OBSTACLE_RADIUS,
        OBSTACLE_Y - OBSTACLE_RADIUS,
        OBSTACLE_X + OBSTACLE_RADIUS,
        OBSTACLE_Y + OBSTACLE_RADIUS
    ], fill=OBSTACLE_COLOR)

    # Draw boids
    for i in range(len(positions)):
        x, y = positions[i]
        vx, vy = velocities[i]
        angle = np.arctan2(vy, vx)
        draw_triangle(draw, x, y, angle, BOID_SIZE, BOID_COLOR)

    return np.array(image)

def run_simulation():
    """Run the simulation with obstacle."""
    print("Running boids with obstacle avoidance...")
    positions, velocities = initialize_boids(NUM_BOIDS)

    frames = []
    for frame_num in range(NUM_FRAMES):
        frame = render_frame(positions, velocities)
        frames.append(frame)
        positions, velocities = update_boids(positions, velocities)

        if (frame_num + 1) % 20 == 0:
            print(f"  Frame {frame_num + 1}/{NUM_FRAMES}")

    output_path = os.path.join(SCRIPT_DIR, 'boids_obstacle.gif')
    imageio.mimsave(output_path, frames, fps=FPS, loop=0)
    print(f"Saved {output_path}")

if __name__ == '__main__':
    run_simulation()
