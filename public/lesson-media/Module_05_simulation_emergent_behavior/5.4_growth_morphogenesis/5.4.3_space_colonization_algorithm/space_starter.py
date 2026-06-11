"""
space_starter.py - Exercise 3 scaffold for Space Colonization.

Setup, rendering, and the main loop are wired up. You implement the
per-frame "find closest node for each attractor, average direction,
spawn new nodes" logic in `grow_step()`.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 560, 560
NUM_ATTRACTORS = 1000
NUM_FRAMES = 90
FPS = 20
SEGMENT_LENGTH = 5.0
KILL_RADIUS = 7.0
INFLUENCE_RADIUS = 70.0


def grow_step(nodes, parents, attractors, consumed):
    """TODO: implement one growth iteration.

    1. Get the indices of active (not-yet-consumed) attractors.
    2. For each active attractor: find the closest node. If that distance
       is greater than INFLUENCE_RADIUS, ignore. Otherwise contribute a
       UNIT VECTOR from that node toward the attractor.
    3. For each node that has any contributors, take the mean direction
       (re-normalised) and spawn a new node at distance SEGMENT_LENGTH.
    4. After all spawns, set consumed[a] = True for any attractor whose
       distance to the nearest (possibly new) node is < KILL_RADIUS.
    """
    return nodes, parents, consumed


def render(nodes, parents, attractors, consumed):
    img = Image.new('RGB', (WIDTH, HEIGHT), (8, 12, 20))
    draw = ImageDraw.Draw(img)
    for atr, used in zip(attractors, consumed):
        if not used:
            draw.point(tuple(atr), fill=(60, 90, 140))
    for i in range(1, len(nodes)):
        p = parents[i]
        if p < 0: continue
        draw.line([tuple(nodes[p]), tuple(nodes[i])],
                  fill=(180, 230, 255), width=2)
    return np.array(img)


def main():
    rng = np.random.default_rng(7)
    attractors = []
    while len(attractors) < NUM_ATTRACTORS:
        r = rng.uniform(20, 230)
        a = rng.uniform(np.pi * 0.05, np.pi * 0.95)
        attractors.append((WIDTH / 2 + r * np.cos(-a + np.pi),
                           HEIGHT - 30 - r * np.sin(a) * 0.8))
    attractors = np.array(attractors)
    nodes = [np.array([WIDTH / 2, HEIGHT - 30])]
    parents = [-1]
    consumed = np.zeros(len(attractors), dtype=bool)
    frames = []
    for _ in range(NUM_FRAMES):
        nodes, parents, consumed = grow_step(nodes, parents, attractors, consumed)
        frames.append(render(nodes, parents, attractors, consumed))
    imageio.mimsave('space_starter.gif', frames, fps=FPS)


if __name__ == '__main__':
    main()
