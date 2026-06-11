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
BACKGROUND_COLOR = (20, 20, 30)

# Boid settings
NUM_BOIDS = 50
BOID_COLOR = (0, 200, 200)
BOID_SIZE = 8

# Behavior parameters
SEPARATION_WEIGHT = 1.5
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0
PERCEPTION_RADIUS = 50
MAX_SPEED = 4
MAX_FORCE = 0.3

# Obstacle settings (NEW)
OBSTACLE_X = WIDTH // 2      # Center X position
OBSTACLE_Y = HEIGHT // 2     # Center Y position
OBSTACLE_RADIUS = 60         # Radius of obstacle
OBSTACLE_COLOR = (180, 60, 60)  # Red color
OBSTACLE_AVOIDANCE_WEIGHT = 2.0  # Strength of avoidance

# Animation settings
NUM_FRAMES = 180
FPS = 30

# =============================================================================
# Data Table Class (Same as main script)
# =============================================================================

class BoidsDataTable:
    """Simulates a TouchDesigner Table DAT storing boid state."""

    def __init__(self, num_boids):
        self.num_boids = num_boids
        self.pos_x = np.random.rand(num_boids) * WIDTH
        self.pos_y = np.random.rand(num_boids) * HEIGHT
        angles = np.random.rand(num_boids) * 2 * np.pi
        speeds = np.random.rand(num_boids) * 2 + 1
        self.vel_x = np.cos(angles) * speeds
        self.vel_y = np.sin(angles) * speeds

    def get_positions(self):
        return np.column_stack([self.pos_x, self.pos_y])

    def get_velocities(self):
        return np.column_stack([self.vel_x, self.vel_y])

    def set_positions(self, positions):
        self.pos_x = positions[:, 0]
        self.pos_y = positions[:, 1]

    def set_velocities(self, velocities):
        self.vel_x = velocities[:, 0]
        self.vel_y = velocities[:, 1]

# =============================================================================
# Physics Functions (Provided - Do not modify)
# =============================================================================

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

def separation_force(positions, distances, differences):
    """Rule 1: Steer away from nearby boids."""
    steering = np.zeros_like(positions)
    for i in range(len(positions)):
        close_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS / 2)
        if np.any(close_mask):
            away_vectors = -differences[i, close_mask]
            weights = 1 / (distances[i, close_mask] + 0.1)
            steering[i] = np.sum(away_vectors * weights[:, np.newaxis], axis=0)
    return steering

def alignment_force(velocities, distances):
    """Rule 2: Match velocity with nearby boids."""
    steering = np.zeros_like(velocities)
    for i in range(len(velocities)):
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)
        if np.any(neighbor_mask):
            average_velocity = np.mean(velocities[neighbor_mask], axis=0)
            steering[i] = average_velocity - velocities[i]
    return steering

def cohesion_force(positions, distances, differences):
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
# TODO: Implement Obstacle Avoidance
# =============================================================================

def obstacle_avoidance(positions):
    """
    Rule 4: Steer away from the central obstacle.

    YOUR TASK: Implement this function to make boids avoid the obstacle.

    Args:
        positions: Array of shape (num_boids, 2) with x, y coordinates

    Returns:
        steering: Array of shape (num_boids, 2) with avoidance forces

    REQUIREMENTS:
    1. Calculate the distance from each boid to the obstacle center
    2. If distance < OBSTACLE_RADIUS * 1.5, apply an avoidance force
    3. The force should point away from the obstacle center
    4. The force should be stronger when the boid is closer

    HINTS:
    - Obstacle center is at (OBSTACLE_X, OBSTACLE_Y)
    - Use OBSTACLE_RADIUS * 1.5 as the avoidance threshold
    - Force direction = normalized vector from obstacle to boid
    - Force strength = inversely proportional to distance
    """
    steering = np.zeros_like(positions)

    # TODO: Implement obstacle avoidance here
    # ---------------------------------------------------------------------
    # Step 1: Define the obstacle center as a numpy array
    # obstacle_center = np.array([OBSTACLE_X, OBSTACLE_Y])

    # Step 2: For each boid, calculate the direction vector from obstacle to boid
    # direction = positions[i] - obstacle_center

    # Step 3: Calculate the distance to the obstacle
    # distance = np.sqrt(np.sum(direction ** 2))

    # Step 4: If within avoidance range, calculate steering force
    # if distance < OBSTACLE_RADIUS * 1.5 and distance > 0:
    #     normalized = direction / distance
    #     strength = (OBSTACLE_RADIUS * 1.5 - distance) / distance
    #     steering[i] = normalized * strength
    # ---------------------------------------------------------------------

    return steering

# =============================================================================
# Physics Update (Modified to include obstacle avoidance)
# =============================================================================

def compute_boids_physics(data_table):
    """
    Main physics computation with obstacle avoidance.

    This function now includes the obstacle_avoidance force
    in addition to the three standard boids rules.
    """
    positions = data_table.get_positions()
    velocities = data_table.get_velocities()

    distances, differences = compute_distances(positions)

    # Calculate all four forces
    sep_force = separation_force(positions, distances, differences)
    ali_force = alignment_force(velocities, distances)
    coh_force = cohesion_force(positions, distances, differences)
    obs_force = obstacle_avoidance(positions)  # NEW: Your implementation

    # Combine forces with weights
    acceleration = (
        sep_force * SEPARATION_WEIGHT +
        ali_force * ALIGNMENT_WEIGHT +
        coh_force * COHESION_WEIGHT +
        obs_force * OBSTACLE_AVOIDANCE_WEIGHT  # NEW: Include obstacle force
    )

    acceleration = limit_magnitude(acceleration, MAX_FORCE)
    velocities = velocities + acceleration
    velocities = limit_magnitude(velocities, MAX_SPEED)
    positions = positions + velocities
    positions[:, 0] = positions[:, 0] % WIDTH
    positions[:, 1] = positions[:, 1] % HEIGHT

    data_table.set_positions(positions)
    data_table.set_velocities(velocities)

    return data_table

# =============================================================================
# Rendering (Modified to draw obstacle)
# =============================================================================

def draw_triangle(draw, x, y, angle, size, color):
    """Draw a triangle pointing in the given direction."""
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

def render_frame(data_table):
    """Render one frame including the obstacle."""
    image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    # Draw the obstacle (red circle)
    draw.ellipse([
        OBSTACLE_X - OBSTACLE_RADIUS,
        OBSTACLE_Y - OBSTACLE_RADIUS,
        OBSTACLE_X + OBSTACLE_RADIUS,
        OBSTACLE_Y + OBSTACLE_RADIUS
    ], fill=OBSTACLE_COLOR)

    # Draw avoidance zone (faint ring showing 1.5x radius)
    avoidance_radius = int(OBSTACLE_RADIUS * 1.5)
    draw.ellipse([
        OBSTACLE_X - avoidance_radius,
        OBSTACLE_Y - avoidance_radius,
        OBSTACLE_X + avoidance_radius,
        OBSTACLE_Y + avoidance_radius
    ], outline=(100, 40, 40), width=1)

    # Draw boids
    positions = data_table.get_positions()
    velocities = data_table.get_velocities()

    for i in range(len(positions)):
        x, y = positions[i]
        vx, vy = velocities[i]
        angle = np.arctan2(vy, vx)
        draw_triangle(draw, x, y, angle, BOID_SIZE, BOID_COLOR)

    return np.array(image)

# =============================================================================
# Main Simulation
# =============================================================================

def run_simulation():
    """Run the boids simulation with obstacle avoidance."""
    print("=" * 60)
    print("Boids with Obstacle Avoidance - Synthesis Project")
    print("=" * 60)

    print("\nInitializing simulation...")
    data_table = BoidsDataTable(NUM_BOIDS)

    frames = []

    print(f"Running {NUM_FRAMES} frames...")
    for frame_num in range(NUM_FRAMES):
        frame = render_frame(data_table)
        frames.append(frame)

        if frame_num == 20:
            frame_path = os.path.join(SCRIPT_DIR, 'boids_obstacle_frame.png')
            Image.fromarray(frame).save(frame_path)
            print(f"Saved snapshot: boids_obstacle_frame.png")

        data_table = compute_boids_physics(data_table)

        if (frame_num + 1) % 30 == 0:
            print(f"Frame {frame_num + 1}/{NUM_FRAMES}")

    print("\nSaving animation...")
    gif_path = os.path.join(SCRIPT_DIR, 'boids_obstacle_demo.gif')
    imageio.mimsave(gif_path, frames, fps=FPS, loop=0)
    print(f"Saved: boids_obstacle_demo.gif")

    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)

    # Check if obstacle avoidance is implemented
    test_positions = np.array([[OBSTACLE_X + OBSTACLE_RADIUS, OBSTACLE_Y]])
    test_result = obstacle_avoidance(test_positions)
    if np.all(test_result == 0):
        print("\nNOTE: obstacle_avoidance() returns zeros.")
        print("Implement the function to see boids avoid the obstacle!")
    else:
        print("\nObstacle avoidance is working!")
        print("Watch the animation to see boids steering around the obstacle.")

if __name__ == '__main__':
    run_simulation()
