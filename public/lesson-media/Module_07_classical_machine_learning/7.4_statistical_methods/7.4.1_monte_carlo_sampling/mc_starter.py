"""
mc_starter.py - Implement Monte Carlo integration from scratch.

Pixels2GenAI Project
"""

import numpy as np


def monte_carlo_integral(f, dim, num_samples, rng):
    """TODO: estimate integral of f over [0, 1]^dim.

    1. Sample num_samples points uniformly from [0, 1]^dim.
    2. Evaluate f at each one.
    3. Return mean of f(sample).
    """
    return 0.0


def main():
    rng = np.random.default_rng(0)

    # f(x) = 4 / (1 + x^2) — integral over [0,1] equals pi
    f1 = lambda x: 4.0 / (1.0 + x[..., 0] ** 2)
    pi_est = monte_carlo_integral(f1, dim=1, num_samples=100_000, rng=rng)
    print(f'Estimate of pi: {pi_est:.4f}  (true: {np.pi:.4f})')


if __name__ == '__main__':
    main()
