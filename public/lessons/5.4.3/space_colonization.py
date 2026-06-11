"""
space_colonization.py - Runions et al. (2007) Space Colonization Algorithm
for generating branching structures. Scatter "attractors" (potential growth
targets) in a 2D area. The tree grows toward whichever attractors are
closer to it than to any other tree node, dropping each attractor once it
is consumed.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 560, 560
NUM_ATTRACTORS = 1400
NUM_FRAMES = 110
FPS = 20
SEGMENT_LENGTH = 5.0
KILL_RADIUS = 7.0          # attractor consumed when this close to a node
INFLUENCE_RADIUS = 70.0    # attractor influences nodes only within this radius
BG = (8, 12, 20)
BRANCH_COLOUR = (180, 230, 255)
SEED_COLOUR = (255, 200, 100)
# ----------------------------


def main():
    rng = np.random.default_rng(7)
    # Disc of attractors in upper half of canvas
    attractors = []
    while len(attractors) < NUM_ATTRACTORS:
        r = rng.uniform(20, 250)
        a = rng.uniform(np.pi * 0.05, np.pi * 0.95)
        attractors.append((WIDTH / 2 + r * np.cos(-a + np.pi), HEIGHT - 30 - r * np.sin(a) * 0.8))
    attractors = np.array(attractors)

    # Start with one root node at the bottom centre
    nodes = [np.array([WIDTH / 2, HEIGHT - 30])]
    parents = [-1]    # index of parent node, -1 for root

    frames = []
    consumed = np.zeros(len(attractors), dtype=bool)

    for frame in range(NUM_FRAMES):
        nodes_arr = np.array(nodes)
        active_idx = np.where(~consumed)[0]
        if len(active_idx) == 0:
            # nothing more to grow toward; just freeze
            frames.append(render(nodes, parents, attractors, consumed))
            continue

        # For each remaining attractor, find its closest node
        deltas = attractors[active_idx][:, None, :] - nodes_arr[None, :, :]
        dist = np.linalg.norm(deltas, axis=-1)
        closest_node = dist.argmin(axis=1)
        min_dist = dist.min(axis=1)

        # accumulate growth direction per node from influencing attractors
        directions = {i: [] for i in range(len(nodes))}
        for atr_local, (cn, d) in enumerate(zip(closest_node, min_dist)):
            if d > INFLUENCE_RADIUS:
                continue
            atr_idx = active_idx[atr_local]
            v = attractors[atr_idx] - nodes_arr[cn]
            directions[cn].append(v / (np.linalg.norm(v) + 1e-6))

        # spawn a new node from each parent that has any direction influence
        new_nodes = []
        new_parents = []
        for cn, dirs in directions.items():
            if not dirs:
                continue
            mean_dir = np.array(dirs).mean(axis=0)
            mean_dir = mean_dir / (np.linalg.norm(mean_dir) + 1e-6)
            new_pt = nodes[cn] + SEGMENT_LENGTH * mean_dir
            new_nodes.append(new_pt)
            new_parents.append(cn)
        nodes.extend(new_nodes)
        parents.extend(new_parents)

        # Consume attractors that are very close to any node
        new_nodes_arr = np.array(nodes)
        for atr_local in active_idx:
            d = np.linalg.norm(new_nodes_arr - attractors[atr_local], axis=-1).min()
            if d < KILL_RADIUS:
                consumed[atr_local] = True

        frames.append(render(nodes, parents, attractors, consumed))
        if frame == NUM_FRAMES - 1:
            Image.fromarray(frames[-1]).save('space_colonization_final.png')

    imageio.mimsave('space_colonization.gif', frames, fps=FPS)
    print(f'Wrote space_colonization.gif (final nodes {len(nodes)})')


def render(nodes, parents, attractors, consumed):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    # Draw remaining attractors as dim dots
    for atr, used in zip(attractors, consumed):
        if used:
            continue
        x, y = atr
        draw.point((x, y), fill=(60, 90, 140))
    # Draw tree segments
    for i in range(1, len(nodes)):
        p = parents[i]
        if p < 0:
            continue
        draw.line([tuple(nodes[p]), tuple(nodes[i])], fill=BRANCH_COLOUR, width=2)
    # Draw root
    x, y = nodes[0]
    draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=SEED_COLOUR)
    return np.array(img)


if __name__ == '__main__':
    main()
