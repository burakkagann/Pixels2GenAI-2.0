import numpy as np
from PIL import Image, ImageDraw
import imageio
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# Configuration Parameters (same as Module 5.2.1 for consistency)
# =============================================================================

# Canvas settings
WIDTH = 512
HEIGHT = 512
BACKGROUND_COLOR = (20, 20, 30)  # Dark blue-gray

# Boid settings
NUM_BOIDS = 50
BOID_COLOR = (0, 200, 200)  # Cyan/teal
BOID_SIZE = 8  # Size of triangle

# Behavior parameters
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
# TouchDesigner-Style Data Storage (Simulates DAT Tables)
# =============================================================================
# In TouchDesigner, boid state would be stored in a Table DAT with columns:
# | id | pos_x | pos_y | vel_x | vel_y |
#
# We simulate this with a dictionary of arrays, which mirrors how you would
# access table data in TD Python: op('boids_table')[row, 'pos_x']

class BoidsDataTable:
    """
    Simulates a TouchDesigner Table DAT storing boid state.

    In actual TD, this would be a Table DAT with rows for each boid
    and columns for position/velocity components.
    """

    def __init__(self, num_boids):
        """Initialize boid data table with random positions and velocities."""
        self.num_boids = num_boids

        # Position columns (like TD table columns 'pos_x', 'pos_y')
        self.pos_x = np.random.rand(num_boids) * WIDTH
        self.pos_y = np.random.rand(num_boids) * HEIGHT

        # Velocity columns (like TD table columns 'vel_x', 'vel_y')
        angles = np.random.rand(num_boids) * 2 * np.pi
        speeds = np.random.rand(num_boids) * 2 + 1
        self.vel_x = np.cos(angles) * speeds
        self.vel_y = np.sin(angles) * speeds

    def get_positions(self):
        """Return positions as (N, 2) array for vectorized operations."""
        return np.column_stack([self.pos_x, self.pos_y])

    def get_velocities(self):
        """Return velocities as (N, 2) array for vectorized operations."""
        return np.column_stack([self.vel_x, self.vel_y])

    def set_positions(self, positions):
        """Update positions from (N, 2) array."""
        self.pos_x = positions[:, 0]
        self.pos_y = positions[:, 1]

    def set_velocities(self, velocities):
        """Update velocities from (N, 2) array."""
        self.vel_x = velocities[:, 0]
        self.vel_y = velocities[:, 1]

# =============================================================================
# TouchDesigner-Style Physics Computation (Simulates Script CHOP)
# =============================================================================
# In TouchDesigner, physics would be computed in a Script CHOP or Execute DAT.
# The script reads from input CHOPs/DATs, computes forces, and outputs results.

def compute_distances(positions):
    """
    Compute pairwise distances between all boids.

    In TD, this might use a CHOP-based approach or be computed in Python.
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

def separation_force(positions, distances, differences):
    """
    Rule 1: Steer away from nearby boids to avoid crowding.
    """
    steering = np.zeros_like(positions)

    for i in range(len(positions)):
        # Find boids that are too close (within half perception radius)
        close_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS / 2)

        if np.any(close_mask):
            # Steer away from close neighbors
            away_vectors = -differences[i, close_mask]
            weights = 1 / (distances[i, close_mask] + 0.1)
            steering[i] = np.sum(away_vectors * weights[:, np.newaxis], axis=0)

    return steering

def alignment_force(velocities, distances):
    """
    Rule 2: Match velocity with nearby boids.
    """
    steering = np.zeros_like(velocities)

    for i in range(len(velocities)):
        # Find neighbors within perception radius
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)

        if np.any(neighbor_mask):
            # Average velocity of neighbors
            average_velocity = np.mean(velocities[neighbor_mask], axis=0)
            steering[i] = average_velocity - velocities[i]

    return steering

def cohesion_force(positions, distances, differences):
    """
    Rule 3: Move toward the center of nearby boids.
    """
    steering = np.zeros_like(positions)

    for i in range(len(positions)):
        # Find neighbors within perception radius
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)

        if np.any(neighbor_mask):
            # Average position of neighbors (relative to current boid)
            center_offset = -np.mean(differences[i, neighbor_mask], axis=0)
            steering[i] = center_offset

    return steering

def limit_magnitude(vectors, max_magnitude):
    """Limit the magnitude of vectors to a maximum value."""
    magnitudes = np.sqrt(np.sum(vectors ** 2, axis=1, keepdims=True))
    magnitudes = np.maximum(magnitudes, 0.0001)  # Avoid division by zero
    scale = np.minimum(1.0, max_magnitude / magnitudes)
    return vectors * scale

def compute_boids_physics(data_table):
    """
    Main physics computation function.

    In TouchDesigner, this would be the content of a Script CHOP or Execute DAT.
    It reads boid state, computes forces, and updates the state.

    Args:
        data_table: BoidsDataTable containing current boid state

    Returns:
        Updated data_table with new positions and velocities
    """
    # Read current state from "DAT table"
    positions = data_table.get_positions()
    velocities = data_table.get_velocities()

    # Compute distances between all boids
    distances, differences = compute_distances(positions)

    # Calculate forces from each rule
    sep_force = separation_force(positions, distances, differences)
    ali_force = alignment_force(velocities, distances)
    coh_force = cohesion_force(positions, distances, differences)

    # Combine forces with weights
    acceleration = (
        sep_force * SEPARATION_WEIGHT +
        ali_force * ALIGNMENT_WEIGHT +
        coh_force * COHESION_WEIGHT
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

    # Write results back to "DAT table"
    data_table.set_positions(positions)
    data_table.set_velocities(velocities)

    return data_table

# =============================================================================
# TouchDesigner-Style Rendering (Simulates Instancing + Render TOP)
# =============================================================================
# In TouchDesigner, rendering uses GPU instancing:
# - Point positions from CHOP/DAT feed into Geometry COMP
# - Instance COMP replicates geometry at each point
# - Render TOP outputs the final image
#
# This Python version simulates that visual output.

def draw_triangle(draw, x, y, angle, size, color):
    """
    Draw a triangle pointing in the given direction.

    In TD, this would be a cone or custom geometry instanced at each boid position.
    """
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
    """
    Render one frame of the simulation.

    In TouchDesigner, this would be handled by:
    1. Geometry COMP with instancing enabled
    2. CHOP feeding position/rotation data
    3. Render TOP outputting the final image

    Returns:
        frame: NumPy array of shape (HEIGHT, WIDTH, 3)
    """
    # Create image with background color
    image = Image.new('RGB', (WIDTH, HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    # Get current state from data table
    positions = data_table.get_positions()
    velocities = data_table.get_velocities()

    # Draw each boid as a triangle pointing in velocity direction
    for i in range(len(positions)):
        x, y = positions[i]
        vx, vy = velocities[i]

        # Calculate angle from velocity (rotation for instancing)
        angle = np.arctan2(vy, vx)

        draw_triangle(draw, x, y, angle, BOID_SIZE, BOID_COLOR)

    return np.array(image)

# =============================================================================
# Main Simulation Loop
# =============================================================================

def run_simulation():
    """
    Run the boids simulation demonstrating TouchDesigner-style architecture.

    The simulation flow mirrors TouchDesigner's node graph:
    1. Data Table (DAT) stores boid state
    2. Script CHOP computes physics each frame
    3. Instance + Render creates visual output

    Generates:
        - boids_td_demo.gif: Animated simulation
        - boids_td_frame.png: Single frame for documentation
    """
    print("=" * 60)
    print("Boids Simulation - TouchDesigner Style Architecture")
    print("=" * 60)

    # Initialize boid data table (simulates Table DAT in TD)
    print("\n[1] Initializing Boids Data Table...")
    print(f"    Creating {NUM_BOIDS} boids with random positions/velocities")
    data_table = BoidsDataTable(NUM_BOIDS)

    frames = []

    # Main simulation loop (simulates TD's frame cook cycle)
    print(f"\n[2] Running simulation for {NUM_FRAMES} frames...")
    print("    Each frame: Physics compute -> Render -> Store")

    for frame_num in range(NUM_FRAMES):
        # Render current state (simulates Render TOP)
        frame = render_frame(data_table)
        frames.append(frame)

        # Save a frame for documentation
        if frame_num == 20:
            frame_path = os.path.join(SCRIPT_DIR, 'boids_td_frame.png')
            Image.fromarray(frame).save(frame_path)
            print(f"\n    Saved snapshot: boids_td_frame.png")

        # Compute physics for next frame (simulates Script CHOP)
        data_table = compute_boids_physics(data_table)

        if (frame_num + 1) % 30 == 0:
            print(f"    Frame {frame_num + 1}/{NUM_FRAMES} complete")

    # Save animation
    print("\n[3] Saving animation...")
    gif_path = os.path.join(SCRIPT_DIR, 'boids_td_demo.gif')
    imageio.mimsave(gif_path, frames, fps=FPS, loop=0)
    print(f"    Saved: boids_td_demo.gif ({len(frames)} frames at {FPS} fps)")

    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)
    print("\nIn TouchDesigner, this same simulation would run at 60+ fps")
    print("with GPU-accelerated instancing for thousands of boids.")

if __name__ == '__main__':
    run_simulation()
