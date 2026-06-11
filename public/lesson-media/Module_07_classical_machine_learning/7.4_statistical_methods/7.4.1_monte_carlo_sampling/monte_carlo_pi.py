"""
monte_carlo_pi.py - Two demonstrations of Monte Carlo:

  1. Estimate pi by throwing random darts at a unit square and counting
     how many land inside the inscribed unit circle.
  2. Integrate a function with no closed form (a 4D integral) by
     averaging f(x) over uniformly-sampled x in [0, 1]^4.

Both are exercises in the same primitive: replace an integral by a
sample average.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RANDOM_STATE = 0
BG = '#0a0c18'


def estimate_pi(num_samples, rng):
    """sum(in_circle) / N * 4 → pi as N → infinity."""
    x = rng.uniform(-1, 1, size=num_samples)
    y = rng.uniform(-1, 1, size=num_samples)
    in_circle = (x * x + y * y) <= 1.0
    return 4.0 * in_circle.mean(), x, y, in_circle


def render_pi_scatter():
    rng = np.random.default_rng(RANDOM_STATE)
    pi_est, x, y, in_circle = estimate_pi(3000, rng)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    ax.scatter(x[in_circle], y[in_circle], s=4, c='#ffd366', alpha=0.7)
    ax.scatter(x[~in_circle], y[~in_circle], s=4, c='#80c6ff', alpha=0.7)
    theta = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(theta), np.sin(theta), color='white', linewidth=1.2)
    ax.set_aspect('equal')
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f'Pi estimate from 3000 samples: {pi_est:.4f}  '
                 f'(true: {np.pi:.4f})',
                 color='#dde2ee', fontsize=11)
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('monte_carlo_pi.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_convergence():
    rng = np.random.default_rng(RANDOM_STATE)
    sample_sizes = np.logspace(2, 6, 25).astype(int)
    estimates = []
    for n in sample_sizes:
        est, *_ = estimate_pi(n, rng)
        estimates.append(est)
    estimates = np.array(estimates)
    expected_error = 2.0 / np.sqrt(sample_sizes)

    fig, ax = plt.subplots(figsize=(8, 4.6), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    ax.semilogx(sample_sizes, estimates, color='#80c6ff', linewidth=1.4,
                marker='o', markersize=4, label='estimate')
    ax.axhline(np.pi, color='#ff7a90', linewidth=1.0, linestyle='--',
               label='true pi')
    ax.fill_between(sample_sizes, np.pi - expected_error, np.pi + expected_error,
                    color='#ffd366', alpha=0.2,
                    label=r'$\pm 2 / \sqrt{N}$')
    ax.set_xlabel('Number of samples', color='#dde2ee')
    ax.set_ylabel('Pi estimate', color='#dde2ee')
    ax.set_title('Monte Carlo convergence: error shrinks as 1/sqrt(N)',
                 color='#dde2ee', fontsize=11)
    ax.legend(loc='upper right', facecolor=BG, edgecolor='#3a4258',
              labelcolor='#dde2ee')
    ax.tick_params(colors='#7f879a')
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('monte_carlo_convergence.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_4d_integral():
    """Estimate the integral of |sin(x_0*x_1) + cos(x_2*x_3)| over [0,1]^4."""
    rng = np.random.default_rng(RANDOM_STATE)
    sample_sizes = np.logspace(2, 6, 12).astype(int)
    estimates = []
    for n in sample_sizes:
        x = rng.uniform(0, 1, size=(n, 4))
        f = np.abs(np.sin(x[:, 0] * x[:, 1]) + np.cos(x[:, 2] * x[:, 3]))
        estimates.append(f.mean())

    fig, ax = plt.subplots(figsize=(8, 4.6), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    ax.semilogx(sample_sizes, estimates, color='#a4f0a4', marker='o',
                markersize=4, linewidth=1.4)
    ax.axhline(estimates[-1], color='#ffd366', linestyle='--',
               linewidth=0.8, label=f'estimate at 10^6: {estimates[-1]:.4f}')
    ax.set_xlabel('Number of samples', color='#dde2ee')
    ax.set_ylabel('Integral estimate', color='#dde2ee')
    ax.set_title('Monte Carlo integration of a 4D function with no closed form',
                 color='#dde2ee', fontsize=11)
    ax.legend(loc='upper right', facecolor=BG, edgecolor='#3a4258',
              labelcolor='#dde2ee')
    ax.tick_params(colors='#7f879a')
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('monte_carlo_4d.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    render_pi_scatter()
    render_convergence()
    render_4d_integral()
    print('Wrote monte_carlo_pi.png, monte_carlo_convergence.png, monte_carlo_4d.png')


if __name__ == '__main__':
    main()
