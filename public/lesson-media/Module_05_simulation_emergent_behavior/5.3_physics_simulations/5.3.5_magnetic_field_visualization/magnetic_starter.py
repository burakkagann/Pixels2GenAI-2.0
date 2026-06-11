"""
magnetic_starter.py - Exercise 3 scaffold.

The grid setup, summation loop, and rendering are wired up. You implement
`dipole_field()` - the 2D point-dipole formula.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def dipole_field(X, Y, position, angle, strength):
    """TODO: return Bx, By arrays for the field of a 2D point dipole.

    Formulae:
      dx = X - pos_x;   dy = Y - pos_y
      r2 = dx^2 + dy^2 + small_epsilon
      r  = sqrt(r2)
      mx = strength * cos(angle);   my = strength * sin(angle)
      m_dot_r = mx*dx + my*dy
      Bx = (3 * m_dot_r * dx / r2 - mx) / (r2 * r)
      By = (3 * m_dot_r * dy / r2 - my) / (r2 * r)
    """
    return np.zeros_like(X), np.zeros_like(Y)


def main():
    x = np.linspace(-3, 3, 140)
    y = np.linspace(-2.5, 2.5, 140)
    X, Y = np.meshgrid(x, y)

    dipoles = [
        (np.array([-1.4, 0.0]), 0.0, 1.0),
        (np.array([+1.4, 0.0]), np.pi, 1.0),
    ]

    Bx, By = np.zeros_like(X), np.zeros_like(Y)
    for pos, angle, strength in dipoles:
        bx, by = dipole_field(X, Y, pos, angle, strength)
        Bx += bx
        By += by

    fig, ax = plt.subplots(figsize=(6, 5), dpi=110, facecolor='#0a0c18')
    ax.set_facecolor('#0a0c18')
    ax.streamplot(X, Y, Bx, By, density=1.5, color='#80c0ff', linewidth=0.7)
    ax.set_xticks([]); ax.set_yticks([])
    fig.savefig('magnetic_starter.png', facecolor='#0a0c18')


if __name__ == '__main__':
    main()
