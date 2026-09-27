# =============================================================================
# Configuration Parameters
# =============================================================================
# These can be promoted to custom parameters on the Script CHOP for
# real-time adjustment in TouchDesigner's parameter interface.

WIDTH = 512
HEIGHT = 512
PERCEPTION_RADIUS = 50
SEPARATION_WEIGHT = 1.5
ALIGNMENT_WEIGHT = 1.0
COHESION_WEIGHT = 1.0
MAX_SPEED = 4
MAX_FORCE = 0.3

# =============================================================================
# Script CHOP Callbacks
# =============================================================================

def onCook(scriptOp):
    """
    Main cook callback - called every frame.

    In TouchDesigner, this function executes during the cook cycle.
    It reads input data, computes physics, and writes output channels.

    Args:
        scriptOp: Reference to this Script CHOP operator
    """
    import numpy as np

    # Get number of boids from the number of samples
    num_boids = scriptOp.numSamples

    if num_boids == 0:
        return

    # -------------------------------------------------------------------------
    # Read current state from input channels
    # -------------------------------------------------------------------------
    # In TD, we read from input CHOP channels or from a stored state
    # For persistent state, use storage: scriptOp.storage['positions']

    # Initialize storage on first cook
    if 'positions' not in scriptOp.storage:
        # Random initial positions
        scriptOp.storage['pos_x'] = np.random.rand(num_boids) * WIDTH
        scriptOp.storage['pos_y'] = np.random.rand(num_boids) * HEIGHT

        # Random initial velocities
        angles = np.random.rand(num_boids) * 2 * np.pi
        speeds = np.random.rand(num_boids) * 2 + 1
        scriptOp.storage['vel_x'] = np.cos(angles) * speeds
        scriptOp.storage['vel_y'] = np.sin(angles) * speeds

    # Get current state from storage
    pos_x = scriptOp.storage['pos_x']
    pos_y = scriptOp.storage['pos_y']
    vel_x = scriptOp.storage['vel_x']
    vel_y = scriptOp.storage['vel_y']

    # Stack into arrays for vectorized computation
    positions = np.column_stack([pos_x, pos_y])
    velocities = np.column_stack([vel_x, vel_y])

    # -------------------------------------------------------------------------
    # Compute pairwise distances
    # -------------------------------------------------------------------------
    differences = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]

    # Handle toroidal wrapping (shortest distance)
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

    # -------------------------------------------------------------------------
    # Compute flocking forces
    # -------------------------------------------------------------------------

    # Separation: steer away from close neighbors
    sep_steering = np.zeros_like(positions)
    for i in range(num_boids):
        close_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS / 2)
        if np.any(close_mask):
            away_vectors = -differences[i, close_mask]
            weights = 1 / (distances[i, close_mask] + 0.1)
            sep_steering[i] = np.sum(away_vectors * weights[:, np.newaxis], axis=0)

    # Alignment: match neighbor velocities
    ali_steering = np.zeros_like(positions)
    for i in range(num_boids):
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)
        if np.any(neighbor_mask):
            avg_velocity = np.mean(velocities[neighbor_mask], axis=0)
            ali_steering[i] = avg_velocity - velocities[i]

    # Cohesion: move toward neighbor center
    coh_steering = np.zeros_like(positions)
    for i in range(num_boids):
        neighbor_mask = (distances[i] > 0) & (distances[i] < PERCEPTION_RADIUS)
        if np.any(neighbor_mask):
            center_offset = -np.mean(differences[i, neighbor_mask], axis=0)
            coh_steering[i] = center_offset

    # -------------------------------------------------------------------------
    # Combine forces and update state
    # -------------------------------------------------------------------------

    # Weight and combine forces
    acceleration = (
        sep_steering * SEPARATION_WEIGHT +
        ali_steering * ALIGNMENT_WEIGHT +
        coh_steering * COHESION_WEIGHT
    )

    # Limit acceleration magnitude
    acc_mag = np.sqrt(np.sum(acceleration ** 2, axis=1, keepdims=True))
    acc_mag = np.maximum(acc_mag, 0.0001)
    scale = np.minimum(1.0, MAX_FORCE / acc_mag)
    acceleration = acceleration * scale

    # Update velocity
    velocities = velocities + acceleration
    vel_mag = np.sqrt(np.sum(velocities ** 2, axis=1, keepdims=True))
    vel_mag = np.maximum(vel_mag, 0.0001)
    scale = np.minimum(1.0, MAX_SPEED / vel_mag)
    velocities = velocities * scale

    # Update position with wrapping
    positions = positions + velocities
    positions[:, 0] = positions[:, 0] % WIDTH
    positions[:, 1] = positions[:, 1] % HEIGHT

    # -------------------------------------------------------------------------
    # Store updated state
    # -------------------------------------------------------------------------
    scriptOp.storage['pos_x'] = positions[:, 0]
    scriptOp.storage['pos_y'] = positions[:, 1]
    scriptOp.storage['vel_x'] = velocities[:, 0]
    scriptOp.storage['vel_y'] = velocities[:, 1]

    # -------------------------------------------------------------------------
    # Write output channels
    # -------------------------------------------------------------------------
    # These channels feed into CHOP To SOP for point generation

    scriptOp.clear()

    # Position channels (for instancing)
    pos_x_chan = scriptOp.appendChan('pos_x')
    pos_y_chan = scriptOp.appendChan('pos_y')
    pos_z_chan = scriptOp.appendChan('pos_z')  # Z = 0 for 2D

    # Rotation channel (for orienting boid geometry)
    rot_z_chan = scriptOp.appendChan('rot_z')

    # Velocity channels (optional, for visualization)
    vel_x_chan = scriptOp.appendChan('vel_x')
    vel_y_chan = scriptOp.appendChan('vel_y')

    for i in range(num_boids):
        pos_x_chan[i] = positions[i, 0]
        pos_y_chan[i] = positions[i, 1]
        pos_z_chan[i] = 0

        # Calculate rotation from velocity (degrees for TD)
        angle_rad = np.arctan2(velocities[i, 1], velocities[i, 0])
        rot_z_chan[i] = np.degrees(angle_rad)

        vel_x_chan[i] = velocities[i, 0]
        vel_y_chan[i] = velocities[i, 1]

def onSetupParameters(scriptOp):
    """
    Called when the Script CHOP is created.
    Use this to add custom parameters for real-time control.
    """
    # Example: Add parameter pages for interactive control
    # page = scriptOp.appendCustomPage('Boids')
    # page.appendFloat('Perceptionradius', label='Perception Radius', default=50)
    # page.appendFloat('Separationweight', label='Separation Weight', default=1.5)
    pass

def onPulse(par):
    """
    Called when a pulse parameter is triggered.
    Can be used to reset the simulation.
    """
    pass

# =============================================================================
# Usage Instructions for TouchDesigner
# =============================================================================
"""
STEP-BY-STEP TOUCHDESIGNER SETUP:

1. CREATE THE NETWORK:
   - Add a Script CHOP
   - Set 'Number of Samples' parameter to 50 (or desired boid count)
   - Paste this code into the Script CHOP

2. CONVERT TO POINTS:
   - Add a CHOP To SOP after the Script CHOP
   - This creates a point cloud from the channel data

3. SET UP INSTANCING:
   - Add a Geometry COMP
   - Inside, create a Cone SOP (or custom boid shape)
   - On the Geometry COMP, enable Instancing
   - Set Instance CHOP to point to your Script CHOP
   - Map tx/ty/tz to pos_x/pos_y/pos_z
   - Map rz to rot_z

4. RENDER:
   - Add a Render TOP
   - Add a Camera COMP positioned to view the scene
   - Add a Light COMP

5. OPTIMIZE:
   - For more boids, consider using GLSL for physics computation
   - Use GPU instancing for rendering thousands of agents
   - Profile with Performance Monitor (Alt+Y)

PARAMETER PROMOTION:
To make parameters adjustable in real-time, promote the constants
at the top of this script to custom parameters on the Script CHOP.
Then reference them as: op('script1').par.Perceptionradius
"""
