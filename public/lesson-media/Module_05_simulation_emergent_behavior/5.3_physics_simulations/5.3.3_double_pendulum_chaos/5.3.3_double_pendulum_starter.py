import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# Physical parameters - experiment with these values
L1 = 1.0        # Length of first pendulum (meters)
L2 = 1.0        # Length of second pendulum (meters)
m1 = 1.0        # Mass of first bob (kg)
m2 = 1.0        # Mass of second bob (kg)
g = 9.81        # Gravitational acceleration (m/s^2)

# Starting positions
theta1_init = np.pi / 2   # First pendulum at 90 degrees
theta2_init = np.pi / 2   # Second pendulum at 90 degrees
omega1_init = 0.0         # Starting at rest
omega2_init = 0.0

# Simulation settings
dt = 0.01
total_time = 10.0
num_steps = int(total_time / dt)

# TODO: Implement the physics equations
def compute_accelerations(theta1, omega1, theta2, omega2):
    """
    Calculate angular accelerations for both pendulums.

    Hints:
    1. First calculate delta_theta = theta1 - theta2
    2. The denominator is: 2*m1 + m2 - m2*cos(2*delta_theta)
    3. Use the coupled differential equations for alpha1 and alpha2
    """
    # YOUR CODE HERE
    # delta_theta = ...
    # denominator = ...
    # alpha1 = ...
    # alpha2 = ...

    pass  # Remove this when you add your code

# TODO: Implement Runge-Kutta 4 integration
def rk4_step(theta1, omega1, theta2, omega2, dt):
    """
    Advance the simulation by one time step using RK4.

    Hints:
    - k1 uses the current state
    - k2 uses state + k1*dt/2
    - k3 uses state + k2*dt/2
    - k4 uses state + k3*dt
    - Combine with: (k1 + 2*k2 + 2*k3 + k4) * dt / 6
    """
    # YOUR CODE HERE

    pass  # Remove this when you add your code

# The rest of the code is provided for you

def run_simulation():
    """Run the simulation and return position history."""
    x1_history = np.zeros(num_steps)
    y1_history = np.zeros(num_steps)
    x2_history = np.zeros(num_steps)
    y2_history = np.zeros(num_steps)

    theta1, omega1 = theta1_init, omega1_init
    theta2, omega2 = theta2_init, omega2_init

    for i in range(num_steps):
        # Convert angles to coordinates
        x1 = L1 * np.sin(theta1)
        y1 = L1 * np.cos(theta1)
        x2 = x1 + L2 * np.sin(theta2)
        y2 = y1 + L2 * np.cos(theta2)

        x1_history[i] = x1
        y1_history[i] = y1
        x2_history[i] = x2
        y2_history[i] = y2

        # Update state
        result = rk4_step(theta1, omega1, theta2, omega2, dt)
        if result is None:
            print("ERROR: rk4_step() returned None. Implement the function first!")
            return None
        theta1, omega1, theta2, omega2 = result

    return x1_history, y1_history, x2_history, y2_history

def create_frame(x1, y1, x2, y2, trail_x, trail_y, frame_size=600, scale=120):
    """Create a single animation frame."""
    image = Image.new('RGB', (frame_size, frame_size), (20, 20, 30))
    draw = ImageDraw.Draw(image)

    center_x = frame_size // 2
    center_y = frame_size // 3

    def to_pixels(x, y):
        return int(center_x + x * scale), int(center_y + y * scale)

    # Draw trail
    if len(trail_x) > 1:
        for i in range(len(trail_x) - 1):
            alpha = int(100 + 155 * (i / len(trail_x)))
            color = (alpha, alpha // 2, alpha)
            px1, py1 = to_pixels(trail_x[i], trail_y[i])
            px2, py2 = to_pixels(trail_x[i + 1], trail_y[i + 1])
            draw.line([(px1, py1), (px2, py2)], fill=color, width=2)

    # Draw pendulum
    pivot = to_pixels(0, 0)
    bob1 = to_pixels(x1, y1)
    bob2 = to_pixels(x2, y2)

    draw.ellipse([pivot[0]-5, pivot[1]-5, pivot[0]+5, pivot[1]+5],
                 fill=(100, 100, 100))
    draw.line([pivot, bob1], fill=(200, 200, 200), width=3)
    draw.line([bob1, bob2], fill=(200, 200, 200), width=3)
    draw.ellipse([bob1[0]-12, bob1[1]-12, bob1[0]+12, bob1[1]+12],
                 fill=(220, 80, 80))
    draw.ellipse([bob2[0]-10, bob2[1]-10, bob2[0]+10, bob2[1]+10],
                 fill=(80, 150, 220))

    return image

def create_animation(x1_hist, y1_hist, x2_hist, y2_hist, filename='my_pendulum.gif'):
    """Create an animated GIF."""
    frames = []
    trail_length = 100

    for i in range(0, len(x1_hist), 3):
        trail_start = max(0, i - trail_length)
        trail_x = x2_hist[trail_start:i+1]
        trail_y = y2_hist[trail_start:i+1]

        frame = create_frame(
            x1_hist[i], y1_hist[i], x2_hist[i], y2_hist[i],
            trail_x, trail_y
        )
        frames.append(np.array(frame))

    imageio.mimsave(filename, frames, fps=30, loop=0)
    print(f"Saved: {filename}")

if __name__ == '__main__':
    print("Double Pendulum Starter")
    print("Implement the TODOs to see your simulation!")
    print()

    result = run_simulation()
    if result is not None:
        x1, y1, x2, y2 = result
        print("Creating animation...")
        create_animation(x1, y1, x2, y2)
        print("Done!")
