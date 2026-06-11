import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# Physical parameters - feel free to experiment with these values
L1 = 1.0        # Length of first pendulum (meters)
L2 = 1.0        # Length of second pendulum (meters)
m1 = 1.0        # Mass of first bob (kg)
m2 = 1.0        # Mass of second bob (kg)
g = 9.81        # Gravitational acceleration (m/s^2)

# Starting positions - try changing these to see different behavior
theta1_init = np.pi / 2   # First pendulum starts at 90 degrees
theta2_init = np.pi / 2   # Second pendulum starts at 90 degrees
omega1_init = 0.0         # First pendulum starts at rest
omega2_init = 0.0         # Second pendulum starts at rest

# Simulation settings
dt = 0.01                 # Time step (smaller = more accurate)
total_time = 30.0         # How long to simulate (seconds)
num_steps = int(total_time / dt)

def compute_accelerations(theta1, omega1, theta2, omega2):
    """
    Lagrangian-derived equations of motion for coupled pendulums.
    See: Goldstein et al. (2002), Section 1.6
    """
    delta_theta = theta1 - theta2

    # This denominator appears in both equations due to the coupling
    denominator = 2 * m1 + m2 - m2 * np.cos(2 * delta_theta)

    # First pendulum acceleration
    numerator1 = (-g * (2 * m1 + m2) * np.sin(theta1)
                  - m2 * g * np.sin(theta1 - 2 * theta2)
                  - 2 * np.sin(delta_theta) * m2
                  * (omega2**2 * L2 + omega1**2 * L1 * np.cos(delta_theta)))
    alpha1 = numerator1 / (L1 * denominator)

    # Second pendulum acceleration
    numerator2 = (2 * np.sin(delta_theta)
                  * (omega1**2 * L1 * (m1 + m2)
                     + g * (m1 + m2) * np.cos(theta1)
                     + omega2**2 * L2 * m2 * np.cos(delta_theta)))
    alpha2 = numerator2 / (L2 * denominator)

    return alpha1, alpha2

def rk4_step(theta1, omega1, theta2, omega2, dt):
    """
    Fourth-order Runge-Kutta integration step.
    See: Press et al. (2007), Section 17.1
    """
    def derivatives(th1, w1, th2, w2):
        a1, a2 = compute_accelerations(th1, w1, th2, w2)
        return w1, a1, w2, a2

    # Sample derivatives at 4 points
    k1 = derivatives(theta1, omega1, theta2, omega2)

    k2 = derivatives(theta1 + k1[0]*dt/2, omega1 + k1[1]*dt/2,
                     theta2 + k1[2]*dt/2, omega2 + k1[3]*dt/2)

    k3 = derivatives(theta1 + k2[0]*dt/2, omega1 + k2[1]*dt/2,
                     theta2 + k2[2]*dt/2, omega2 + k2[3]*dt/2)

    k4 = derivatives(theta1 + k3[0]*dt, omega1 + k3[1]*dt,
                     theta2 + k3[2]*dt, omega2 + k3[3]*dt)

    # Combine the samples with RK4 weights
    theta1_new = theta1 + (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * dt / 6
    omega1_new = omega1 + (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * dt / 6
    theta2_new = theta2 + (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]) * dt / 6
    omega2_new = omega2 + (k1[3] + 2*k2[3] + 2*k3[3] + k4[3]) * dt / 6

    return theta1_new, omega1_new, theta2_new, omega2_new

def run_simulation(theta1_0, omega1_0, theta2_0, omega2_0):
    """Run the full simulation and return position history."""
    # Arrays to store the path of each bob
    x1_history = np.zeros(num_steps)
    y1_history = np.zeros(num_steps)
    x2_history = np.zeros(num_steps)
    y2_history = np.zeros(num_steps)

    theta1, omega1, theta2, omega2 = theta1_0, omega1_0, theta2_0, omega2_0

    for i in range(num_steps):
        # Convert angles to x,y coordinates (origin at pivot, y points down)
        x1 = L1 * np.sin(theta1)
        y1 = L1 * np.cos(theta1)
        x2 = x1 + L2 * np.sin(theta2)
        y2 = y1 + L2 * np.cos(theta2)

        x1_history[i] = x1
        y1_history[i] = y1
        x2_history[i] = x2
        y2_history[i] = y2

        # Step forward in time
        theta1, omega1, theta2, omega2 = rk4_step(
            theta1, omega1, theta2, omega2, dt
        )

    return x1_history, y1_history, x2_history, y2_history

def create_frame(x1, y1, x2, y2, trail_x, trail_y, frame_size=600, scale=120):
    """Create a single frame showing the pendulum and its trail."""
    image = Image.new('RGB', (frame_size, frame_size), (20, 20, 30))
    draw = ImageDraw.Draw(image)

    # Pivot point is near the top center
    center_x = frame_size // 2
    center_y = frame_size // 3

    def to_pixels(x, y):
        return int(center_x + x * scale), int(center_y + y * scale)

    # Draw the trajectory trail with a fade effect
    if len(trail_x) > 1:
        for i in range(len(trail_x) - 1):
            alpha = int(100 + 155 * (i / len(trail_x)))
            color = (alpha, alpha // 2, alpha)
            px1, py1 = to_pixels(trail_x[i], trail_y[i])
            px2, py2 = to_pixels(trail_x[i + 1], trail_y[i + 1])
            draw.line([(px1, py1), (px2, py2)], fill=color, width=2)

    # Draw the pendulum structure
    pivot = to_pixels(0, 0)
    bob1 = to_pixels(x1, y1)
    bob2 = to_pixels(x2, y2)

    # Pivot point
    draw.ellipse([pivot[0]-5, pivot[1]-5, pivot[0]+5, pivot[1]+5],
                 fill=(100, 100, 100))

    # Rods
    draw.line([pivot, bob1], fill=(200, 200, 200), width=3)
    draw.line([bob1, bob2], fill=(200, 200, 200), width=3)

    # Bobs (red for first, blue for second)
    draw.ellipse([bob1[0]-12, bob1[1]-12, bob1[0]+12, bob1[1]+12],
                 fill=(220, 80, 80))
    draw.ellipse([bob2[0]-10, bob2[1]-10, bob2[0]+10, bob2[1]+10],
                 fill=(80, 150, 220))

    return image

def create_animation(x1_hist, y1_hist, x2_hist, y2_hist, filename='double_pendulum.gif'):
    """Create an animated GIF of the pendulum motion."""
    frames = []
    trail_length = 150
    frame_skip = 3  # Skip frames to keep file size reasonable

    for i in range(0, len(x1_hist), frame_skip):
        trail_start = max(0, i - trail_length)
        trail_x = x2_hist[trail_start:i+1]
        trail_y = y2_hist[trail_start:i+1]

        frame = create_frame(
            x1_hist[i], y1_hist[i], x2_hist[i], y2_hist[i],
            trail_x, trail_y
        )
        frames.append(np.array(frame))

    imageio.mimsave(filename, frames, fps=30, loop=0)
    print(f"Saved animation: {filename}")

def create_static_image(x1_hist, y1_hist, x2_hist, y2_hist, filename='double_pendulum_frame.png'):
    """Create a static image showing the pendulum with its trajectory."""
    frame_idx = len(x1_hist) // 2
    trail_x = x2_hist[:frame_idx]
    trail_y = y2_hist[:frame_idx]

    frame = create_frame(
        x1_hist[frame_idx], y1_hist[frame_idx],
        x2_hist[frame_idx], y2_hist[frame_idx],
        trail_x, trail_y
    )
    frame.save(filename)
    print(f"Saved static image: {filename}")

if __name__ == '__main__':
    print("Double Pendulum Chaos Simulation")
    print(f"Parameters: L1={L1}m, L2={L2}m, m1={m1}kg, m2={m2}kg")
    print(f"Initial angles: {np.degrees(theta1_init):.1f} and {np.degrees(theta2_init):.1f} degrees")
    print()

    # Run simulation
    print("Running simulation...")
    x1, y1, x2, y2 = run_simulation(
        theta1_init, omega1_init, theta2_init, omega2_init
    )

    # Generate outputs
    print("Creating animation...")
    create_animation(x1, y1, x2, y2)

    print("Creating static frame...")
    create_static_image(x1, y1, x2, y2)
    
    print("\nDone! Check the output files.")
