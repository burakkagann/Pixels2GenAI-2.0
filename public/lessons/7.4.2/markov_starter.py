"""
markov_starter.py - Train a Markov chain from text and sample from it.

Pixels2GenAI Project
"""

import numpy as np


CORPUS = "the quick brown fox jumps over the lazy dog. " * 6


def build_transition_matrix(text):
    """TODO: count adjacent character pairs, return (chars, transition).

    1. chars = sorted unique characters in text.
    2. Build an integer (n, n) count matrix where counts[i, j] is the
       number of times char j follows char i in text.
    3. Add 1 to every entry (Laplace smoothing) and divide each row by
       its sum so each row sums to 1.
    4. Return (chars list, transition 2D ndarray).
    """
    return [], np.zeros((0, 0))


def sample(transition, chars, length, seed_char, rng):
    """TODO: sample `length` characters from the chain starting at seed_char.

    For each step, pick the next character index by sampling from the
    row of `transition` indexed by the current character.
    """
    return ''


def main():
    rng = np.random.default_rng(0)
    chars, T = build_transition_matrix(CORPUS)
    print(f'vocab size: {len(chars)}')
    if len(chars) > 0:
        print(f'sample: {sample(T, chars, 80, chars[0], rng)}')


if __name__ == '__main__':
    main()
