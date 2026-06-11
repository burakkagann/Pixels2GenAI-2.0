"""
markov_chain.py - A character-level Markov chain trained on a small
text corpus. Sample from it to generate new text that locally looks
like the corpus but has no global structure.

The visual artefact: a heatmap of the transition matrix.

Pixels2GenAI Project
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

RANDOM_STATE = 0
BG = '#0a0c18'


# Small training corpus: assembled famous opening lines + nonsense.
CORPUS = """
it was the best of times, it was the worst of times, it was the age of wisdom,
it was the age of foolishness, it was the epoch of belief, it was the epoch of
incredulity, it was the season of light, it was the season of darkness, it was
the spring of hope, it was the winter of despair. call me ishmael. some years
ago having little or no money in my purse and nothing particular to interest
me on shore i thought i would sail about a little and see the watery part of
the world. all happy families are alike each unhappy family is unhappy in its
own way. happy days are here again the skies above are clear again so let us
sing a song of cheer again happy days are here again.
""".strip().replace('\n', ' ')


def build_transition_matrix(text):
    """Count adjacent character pairs and normalise to a row-stochastic matrix."""
    chars = sorted(set(text))
    idx = {c: i for i, c in enumerate(chars)}
    n = len(chars)
    counts = np.zeros((n, n), dtype=np.float64)
    for a, b in zip(text, text[1:]):
        counts[idx[a], idx[b]] += 1
    counts += 1.0   # Laplace smoothing
    transition = counts / counts.sum(axis=1, keepdims=True)
    return chars, transition


def sample(transition, chars, length, seed_char, rng):
    idx = {c: i for i, c in enumerate(chars)}
    out = [seed_char]
    for _ in range(length - 1):
        row = transition[idx[out[-1]]]
        next_idx = rng.choice(len(chars), p=row)
        out.append(chars[next_idx])
    return ''.join(out)


def render_transition_heatmap(chars, transition):
    n = len(chars)
    fig, ax = plt.subplots(figsize=(7, 7), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    im = ax.imshow(transition, cmap='magma', aspect='equal',
                   norm=matplotlib.colors.PowerNorm(0.35))
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(chars, color='#dde2ee', fontsize=8)
    ax.set_yticklabels(chars, color='#dde2ee', fontsize=8)
    ax.set_xlabel('next character', color='#dde2ee')
    ax.set_ylabel('current character', color='#dde2ee')
    ax.set_title('Character transition matrix', color='#dde2ee', fontsize=11)
    cbar = fig.colorbar(im, ax=ax)
    cbar.ax.tick_params(colors='#7f879a')
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('markov_transition.png', facecolor=BG, dpi=110)
    plt.close(fig)


def render_stationary_distribution(chars, transition):
    """Compute the stationary distribution by repeated multiplication."""
    n = len(chars)
    pi = np.full(n, 1.0 / n)
    for _ in range(2000):
        pi = pi @ transition
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=BG, dpi=110)
    ax.set_facecolor(BG)
    ax.bar(range(n), pi, color='#80c6ff', edgecolor='white', linewidth=0.5)
    ax.set_xticks(range(n))
    ax.set_xticklabels(chars, color='#dde2ee', fontsize=8)
    ax.set_yticks([])
    ax.set_title('Stationary distribution (long-run character frequencies)',
                 color='#dde2ee', fontsize=11)
    for spine in ax.spines.values():
        spine.set_color('#3a4258')
    fig.tight_layout()
    fig.savefig('markov_stationary.png', facecolor=BG, dpi=110)
    plt.close(fig)


def main():
    rng = np.random.default_rng(RANDOM_STATE)
    chars, transition = build_transition_matrix(CORPUS)
    print(f'Vocabulary: {len(chars)} characters')
    print(f'Sample from chain (seed "t"):')
    print(f'  {sample(transition, chars, 240, "t", rng)}')
    render_transition_heatmap(chars, transition)
    render_stationary_distribution(chars, transition)
    print('Wrote markov_transition.png, markov_stationary.png')


if __name__ == '__main__':
    main()
