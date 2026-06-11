"""
magnetic_field.py - Visualise the 2D magnetic field of several point dipoles
by streamline tracing. At each grid point, the field is the vector sum of
each dipole's contribution; streamlines are integral curves of that field.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 400
NUM_FRAMES = 48
FPS = 14

GRID = 160
EXTENT = (-3.0, 3.0, -2.5, 2.5)
# (position, orientation_angle, strength)
INITIAL_DIPOLES = [
    (np.array([-1.4, 0.0]), 0.0, 1.0),
    (np.array([+1.4, 0.0]), np.pi, 1.0),
]
ROTATION_PER_FRAME = 2 * np.pi / NUM_FRAMES
# ----------------------------


def dipole_field(X, Y, position, angle, strength):
    """2D point-dipole field. m = strength * (cos(angle), sin(angle))."""
    dx = X - position[0]
    dy = Y - position[1]
    r2 = dx * dx + dy * dy + 0.02
    r = np.sqrt(r2)
    mx = strength * np.cos(angle)
    my = strength * np.sin(angle)
    m_dot_r = mx * dx + my * dy
    Bx = (3 * m_dot_r * dx / r2 - mx) / (r2 * r)
    By = (3 * m_dot_r * dy / r2 - my) / (r2 * r)
    return Bx, By


def render_field(dipoles, frame_idx):
    xmin, xmax, ymin, ymax = EXTENT
    x = np.linspace(xmin, xmax, GRID)
    y = np.linspace(ymin, ymax, GRID)
    X, Y = np.meshgrid(x, y)
    Bx_total = np.zeros_like(X)
    By_total = np.zeros_like(Y)
    for pos, angle, strength in dipoles:
        Bx, By = dipole_field(X, Y, pos, angle, strength)
        Bx_total += Bx
        By_total += By
    magnitude = np.log1p(np.sqrt(Bx_total**2 + By_total**2))

    fig, ax = plt.subplots(figsize=(WIDTH / 100, HEIGHT / 100), dpi=100)
    ax.set_facecolor('#0a0c18')
    fig.patch.set_facecolor('#0a0c18')
    ax.streamplot(
        X, Y, Bx_total, By_total,
        density=1.6, linewidth=0.9,
        color=magnitude, cmap='cividis',
        arrowsize=0.7,
    )
    for pos, angle, strength in dipoles:
        hx, hy = 0.18 * np.cos(angle), 0.18 * np.sin(angle)
        ax.arrow(pos[0] - hx, pos[1] - hy, 2 * hx, 2 * hy,
                 width=0.08, color='#ffb060', length_includes_head=True)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.text(0.02, 0.96, f'frame {frame_idx:>3}', transform=ax.transAxes,
            color='#aac0d0', fontsize=10, va='top')
    fig.tight_layout(pad=0)
    fig.canvas.draw()
    img = np.asarray(fig.canvas.buffer_rgba())[..., :3].copy()
    plt.close(fig)
    return img


def main():
    dipoles = list(INITIAL_DIPOLES)
    frames = []
    for frame in range(NUM_FRAMES):
        # rotate the right dipole slowly to animate the field
        rotated = []
        for i, (pos, angle, strength) in enumerate(dipoles):
            if i == 1:
                angle = angle + ROTATION_PER_FRAME * frame
            rotated.append((pos, angle, strength))
        img = render_field(rotated, frame)
        frames.append(img)
        if frame == NUM_FRAMES // 2:
            Image.fromarray(img).save('magnetic_frame.png')
    imageio.mimsave('magnetic_field.gif', frames, fps=FPS)
    Image.fromarray(frames[0]).save('magnetic_dipole_pair.png')
    print(f'Wrote magnetic_field.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
