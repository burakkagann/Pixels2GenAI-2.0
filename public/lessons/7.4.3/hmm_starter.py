"""
hmm_starter.py - Implement Viterbi from scratch.

Given an HMM (start_prob, transition, emission) and an observation
sequence, return the most likely sequence of hidden states.

Pixels2GenAI Project
"""

import numpy as np


START_PROB = np.array([0.6, 0.3, 0.1])
TRANSITION = np.array([
    [0.70, 0.20, 0.10],
    [0.30, 0.45, 0.25],
    [0.10, 0.30, 0.60],
])
EMISSION = np.array([
    [0.75, 0.20, 0.05],
    [0.15, 0.65, 0.20],
    [0.05, 0.20, 0.75],
])


def viterbi(obs, start_prob, transition, emission):
    """TODO: implement the Viterbi algorithm.

    delta[t, j] = max over hidden state sequences ending in j of
                  log P(state_sequence, obs[:t+1])
    psi[t, j]   = argmax of the above (the backtracking pointer)

    1. Initialise: delta[0] = log(start_prob) + log(emission[:, obs[0]])
                   psi[0] = 0
    2. For t = 1..T-1:
         For each next-state j:
           scores = delta[t-1] + log(transition[:, j])
           psi[t, j] = scores.argmax()
           delta[t, j] = scores.max() + log(emission[j, obs[t]])
    3. Backtrack: path[T-1] = delta[-1].argmax();
                  path[t]   = psi[t+1, path[t+1]] for t = T-2 .. 0
    """
    return np.zeros(len(obs), dtype=int)


def main():
    obs = [0, 1, 2, 0, 0, 1, 2, 2, 1, 0]
    path = viterbi(obs, START_PROB, TRANSITION, EMISSION)
    print(f'Observations: {obs}')
    print(f'Recovered:    {path.tolist()}')


if __name__ == '__main__':
    main()
