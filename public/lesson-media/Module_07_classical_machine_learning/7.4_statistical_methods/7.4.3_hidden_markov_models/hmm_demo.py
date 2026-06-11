"""
hmm_demo.py - A 3-state Hidden Markov Model with discrete emissions.

The hidden states are weather modes: sunny / cloudy / rainy. The
observations are activity choices: walk / shop / clean. We:

  1. Generate a synthetic sequence by sampling the HMM.
  2. Run the Viterbi algorithm to recover the most likely hidden
     state path from observations alone.
  3. Compare the recovered path to ground truth.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RANDOM_STATE = 0
BG = '#0a0c18'

STATES = ['Sunny', 'Cloudy', 'Rainy']
OBSERVATIONS = ['Walk', 'Shop', 'Clean']

# Hidden state initial distribution
START_PROB = np.array([0.6, 0.3, 0.1])

# Hidden state transition matrix (rows: from, cols: to)
TRANSITION = np.array([
    [0.70, 0.20, 0.10],   # Sunny -> ?
    [0.30, 0.45, 0.25],   # Cloudy -> ?
    [0.10, 0.30, 0.60],   # Rainy -> ?
])

# Emission matrix (rows: hidden state, cols: observation)
EMISSION = np.array([
    [0.75, 0.20, 0.05],   # Sunny: mostly walk
    [0.15, 0.65, 0.20],   # Cloudy: mostly shop
    [0.05, 0.20, 0.75],   # Rainy: mostly clean
])


def sample_hmm(length, rng):
    states = np.zeros(length, dtype=int)
    obs = np.zeros(length, dtype=int)
    states[0] = rng.choice(3, p=START_PROB)
    obs[0] = rng.choice(3, p=EMISSION[states[0]])
    for t in range(1, length):
        states[t] = rng.choice(3, p=TRANSITION[states[t - 1]])
        obs[t] = rng.choice(3, p=EMISSION[states[t]])
    return states, obs


def viterbi(obs):
    """Most likely sequence of hidden states given observations."""
    T = len(obs)
    N = 3
    log_start = np.log(START_PROB + 1e-12)
    log_trans = np.log(TRANSITION + 1e-12)
    log_em = np.log(EMISSION + 1e-12)

    delta = np.full((T, N), -np.inf)
    psi = np.zeros((T, N), dtype=int)
    delta[0] = log_start + log_em[:, obs[0]]
    for t in range(1, T):
        for j in range(N):
            scores = delta[t - 1] + log_trans[:, j]
            psi[t, j] = scores.argmax()
            delta[t, j] = scores.max() + log_em[j, obs[t]]

    path = np.zeros(T, dtype=int)
    path[-1] = delta[-1].argmax()
    for t in range(T - 2, -1, -1):
        path[t] = psi[t + 1, path[t + 1]]
    return path


def render_sequence(states, obs, recovered, n=60):
    fig, ax = plt.subplots(figsize=(11, 4), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    palette = ['#ffd366', '#a4a4a4', '#80c6ff']
    for t in range(n):
        ax.fill_between([t, t + 1], 2, 3,
                        color=palette[states[t]], alpha=0.85)
        ax.fill_between([t, t + 1], 1, 2,
                        color=palette[recovered[t]], alpha=0.85,
                        edgecolor=('#ff7a90' if states[t] != recovered[t] else 'none'),
                        linewidth=1.0)
        ax.text(t + 0.5, 0.5, OBSERVATIONS[obs[t]][0],
                ha='center', va='center', fontsize=8, color='#dde2ee')
    ax.set_xlim(0, n); ax.set_ylim(0, 3)
    ax.set_yticks([0.5, 1.5, 2.5])
    ax.set_yticklabels(['Observation', 'Viterbi state', 'True state'],
                       color='#dde2ee')
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    ax.set_title(f'HMM sequence ({n} timesteps)  ·  '
                 f'pink outlines mark Viterbi errors',
                 color='#dde2ee', fontsize=11)
    fig.tight_layout()
    fig.savefig('hmm_sequence.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_emission_matrix():
    fig, ax = plt.subplots(figsize=(5, 4.5), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    im = ax.imshow(EMISSION, cmap='magma', aspect='auto')
    ax.set_xticks(range(3)); ax.set_yticks(range(3))
    ax.set_xticklabels(OBSERVATIONS, color='#dde2ee')
    ax.set_yticklabels(STATES, color='#dde2ee')
    ax.set_title('Emission matrix\n(hidden state → observation)',
                 color='#dde2ee', fontsize=11)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f'{EMISSION[i, j]:.2f}',
                    ha='center', va='center', color='white', fontsize=10)
    fig.colorbar(im, ax=ax).ax.tick_params(colors='#7f879a')
    fig.tight_layout()
    fig.savefig('hmm_emission.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    rng = np.random.default_rng(RANDOM_STATE)
    states, obs = sample_hmm(200, rng)
    recovered = viterbi(obs)
    acc = (states == recovered).mean()
    render_sequence(states, obs, recovered)
    render_emission_matrix()
    print(f'Viterbi recovery accuracy: {acc:.2%}')
    print('Wrote hmm_sequence.png, hmm_emission.png')


if __name__ == '__main__':
    main()
